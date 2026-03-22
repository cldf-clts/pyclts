"""
Create a distribution of the CLTS dataset in CLDF format for convenient reuse.

Writes:
- CLDF Dataset section of README.md
- cldf-metadata.json
- data/graphemes.tsv
- data/sounds.tsv
- data/features.tsv
- data/clts.zip
"""
import json
import logging
import zipfile
import collections
import dataclasses

from clldutils.clilib import PathType
from clldutils.jsonlib import load, dump
from clldutils.markup import iter_markdown_sections
from pycldf import Dataset
from pycldf.markdown import metadata2markdown

from pyclts.models import Marker
from pyclts.datatypes import TranscriptionSystem, TranscriptionData, SoundClasses
from pyclts.cldf import FeatureTable, SoundTable, GraphemeTable
from pyclts.metadata import Source
from pyclts.cli_util import upsert_section

METADATA = {
    "@context": ["http://www.w3.org/ns/csvw", {"@language": "en"}],
    "dc:conformsTo": "http://cldf.clld.org/v1.0/terms.rdf#Generic",
    "dc:source": "data/references.bib",
    "rdf:ID": "clts",
    "dc:license": "https://creativecommons.org/licenses/by/4.0/",
    "dialect": FeatureTable.__dialect__,
    "tables": [
        Source.cldf_table_spec(),
        FeatureTable.cldf_table_spec(),
        GraphemeTable.cldf_table_spec(),
        SoundTable.cldf_table_spec(),
    ]
}


def register(parser):  # pylint: disable=C0116
    parser.add_argument(
        "--destination",
        default=None,
        type=PathType(type='file', must_exist=False),
        help="Name of the file to store data in compressed form."
    )


@dataclasses.dataclass
class Acc:
    """Accumulator for distribution data."""
    bipa: TranscriptionSystem
    feature_ids: set[str]
    log: logging.Logger
    sounds: dict[str, SoundTable] = dataclasses.field(default_factory=collections.OrderedDict)
    graphemes: list[GraphemeTable] = dataclasses.field(default_factory=list)
    clts_dump: dict[str, tuple[str, str]] = dataclasses.field(
        default_factory=collections.OrderedDict)

    def _add_grapheme(self, **d):
        pk = len(self.graphemes) + 1
        self.graphemes.append(GraphemeTable(PK=str(pk), **d))

    def add_bipa_sounds(self):
        """Add the sounds from the BIPA transcription system."""
        for grapheme, sound in sorted(
            self.bipa.sounds.items(),
            key=lambda p: (p[1].alias if p[1].alias else False, p[0], p[1].uname)
        ):
            if not isinstance(sound, Marker):
                if sound.alias:
                    assert sound.name in self.sounds
                else:
                    assert sound.name not in self.sounds
                    self.sounds[sound.name] = SoundTable.from_grapheme_and_sound(
                        grapheme, sound, self.feature_ids, self.log)
                self._add_grapheme(
                    GRAPHEME=grapheme,
                    NAME=sound.name,
                    EXPLICIT='+',
                    DATASET='bipa',
                    NOTE=sound.note or '')
                if grapheme not in self.clts_dump:
                    self.clts_dump[grapheme] = (str(sound), sound.name)

    def add_transcriptionsystem(self, ts: TranscriptionSystem):
        """Add the graphemes defined for BIPA sounds in other transcription systems."""
        for name, sound in self.sounds.items():
            try:
                ts_sound = ts[name]
                if ts.is_valid(ts_sound):
                    self._add_grapheme(
                        GRAPHEME=ts_sound.s,
                        NAME=name,
                        EXPLICIT='' if sound.GENERATED else '+',
                        DATASET=ts.id,
                    )
                    if ts_sound.s not in self.clts_dump:
                        self.clts_dump[ts_sound.s] = (sound.GRAPHEME, name)
            except ValueError:
                pass
            except TypeError:  # pragma: no cover
                self.log.debug('%s: %s', ts.id, name)

    def add_transcriptiondata(self, td: TranscriptionData):
        """Add sounds and graphemes from transcrption data."""
        for name in td.names:
            bipa_sound = self.bipa[name]

            # check for consistency of mapping here
            if not self.bipa.is_valid(bipa_sound):
                continue

            sound = self.sounds.get(name)
            if not sound:
                sound = self.sounds[name] = SoundTable.from_name_and_sound(
                    name, bipa_sound, self.feature_ids, self.log)

            for item in sorted(td.data[name], key=lambda d: (d['bipa_grapheme'], d['grapheme'])):
                # add the values here
                self._add_grapheme(
                    GRAPHEME=item['grapheme'],
                    NAME=name,
                    EXPLICIT=item['explicit'],
                    DATASET=td.id,
                    FREQUENCY=item.get('frequency', ''),
                    URL=item.get('url', ''),
                    FEATURES=item.get('features', ''),
                    IMAGE=item.get('image', ''),
                    SOUND=item.get('sound', ''),
                )
                if item['grapheme'] not in self.clts_dump:
                    self.clts_dump[item['grapheme']] = (sound.GRAPHEME, name)

    def add_soundclass(self, sc: SoundClasses):
        """Add graphemes described in a soundclass system."""
        for name in sorted(self.sounds):
            try:
                grapheme = sc[name]
                self._add_grapheme(
                    GRAPHEME=grapheme,
                    NAME=name,
                    EXPLICIT='+' if name in sc.data else '',
                    DATASET=sc.id,
                )
            except KeyError:  # pragma: no cover
                self.log.debug(name, self.sounds[name].GRAPHEME)


def run(args):  # pylint: disable=C0116
    args.destination = args.destination or args.repos.path('data', 'clts.zip')

    # Write the feature system to a file and keep the set of feature IDs for reference.
    FeatureTable.write(args.repos)
    fids = FeatureTable.row_ids()

    # Instantitate the accumulator for the distribution data.
    acc = Acc(bipa=args.repos.bipa, feature_ids=set(fids), log=args.log)

    # start with assembling bipa-sounds
    args.log.info('adding bipa data')
    acc.add_bipa_sounds()

    # add sounds systematically by their alias
    args.log.info('adding transcription data')
    for td in args.repos.iter_transcriptiondata():
        acc.add_transcriptiondata(td)

    # sound classes have a generative component, so we need to treat them separately
    args.log.info('adding sound classes')
    for sc in args.repos.iter_soundclass():
        acc.add_soundclass(sc)

    # last run, check again for each of the remaining transcription systems,
    # whether we can translate the sound
    args.log.info('adding remaining transcription systems')
    for ts in args.repos.iter_transcriptionsystem(exclude=['bipa']):
        acc.add_transcriptionsystem(ts)

    args.log.info('writing data to file')

    counts = {
        Source.rel_path(): len(args.repos.meta),
        FeatureTable.rel_path(): len(fids),
        SoundTable.rel_path(): SoundTable.write(
            args.repos, [acc.sounds[k] for k in sorted(acc.sounds, reverse=True)]),
        GraphemeTable.rel_path(): GraphemeTable.write(args.repos, acc.graphemes),
    }
    for table in METADATA['tables']:
        table['dc:extent'] = counts[table['url']]

    METADATA.update(load(args.repos.repos / 'metadata.json'))
    md_path = args.repos.repos / 'cldf-metadata.json'
    dump(METADATA, md_path, indent=4)
    ds = Dataset.from_metadata(md_path)
    args.log.info('running CLDF validation')
    ds.validate(log=args.log)
    md = []
    for level, header, text in iter_markdown_sections(metadata2markdown(ds, md_path)):
        if level == 1:
            md.append(text)
        else:
            md.append('\n#' + header)
            md.append(text)

    upsert_section(args.repos.repos / 'README.md', 'CLDF Dataset', 2, '\n'.join(md))

    with zipfile.ZipFile(args.destination, mode='w', compression=zipfile.ZIP_DEFLATED) as myzip:
        myzip.writestr('clts.json', json.dumps(acc.clts_dump))
