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
import zipfile
import collections

import attr
from csvw.dsv import UnicodeWriter
from clldutils.clilib import PathType
from clldutils.jsonlib import load, dump
from pycldf import Dataset
from pycldf.util import metadata2markdown

from pyclts.models import is_valid_sound
from pyclts.util import upsert_section, iter_markdown_sections

METADATA = {
    "@context": ["http://www.w3.org/ns/csvw", {"@language": "en"}],
    "dc:conformsTo": "http://cldf.clld.org/v1.0/terms.rdf#Generic",
    "dc:source": "data/references.bib",
    "dialect": {"doubleQuote": False, "commentPrefix": None, "delimiter": "\t", "trim": True},
    "tables": [
        {
            "url": "sources/index.tsv",
            "dc:description":
                "CLTS is compiled from information about transcriptions and how these relate to "
                "sounds from many sources, such as phoneme inventory databases like PHOIBLE or "
                "relevant typological surveys.",
            "tableSchema": {
                "columns": [
                    {
                        "name": "NAME",
                        "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id",
                        "datatype": {"base": "string"}
                    },
                    {
                        "name": "DESCRIPTION",
                        "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#description",
                        "datatype": {"base": "string"}
                    },
                    {
                        "name": "REFS",
                        "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#source",
                        "datatype": {"base": "string"},
                        "separator": ", "
                    },
                    {
                        "name": "TYPE",
                        "dc:description":
                            "CLTS groups transcription information into three categories: "
                            "Transcription systems (`ts`), transcription data (`td`) and "
                            "soundclass systems (`sc`).",
                        "datatype": {"base": "string", "format": "td|ts|sc"}
                    },
                    {
                        "name": "URITEMPLATE",
                        "dc:description":
                            "Several CLTS sources provide an online catalog of the graphemes they "
                            "describe. If this is the case, the URI template specified in this "
                            "column was used to derive the URL column in graphemes.csv.",
                        "datatype": {"base": "string"}
                    }
                ],
                "primaryKey": ["NAME"]
            }
        },
        {
            "url": "data/features.tsv",
            "dc:description":
                "The feature system employed by CLTS describes sounds by assigning values for "
                "certain features (constrained by sound type). The permissible values per "
                "(feature, sound type) are listed in this table.",
            "tableSchema": {
                "columns": [
                    {
                        "name": "ID",
                        "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id",
                        "datatype": {"base": "string"}
                    },
                    {
                        "name": "TYPE",
                        "dc:description":
                            "CLTS distinguishes the basic sound types consonant, vowel, tone, "
                            "and marker. Features are defined for consonants, vowels, and tones.",
                        "datatype": {"base": "string", "format": "consonant|vowel|tone"}
                    },
                    {
                        "name": "FEATURE",
                        "dc:description": "Note that CLTS features are not necessarily binary.",
                        "datatype": {"base": "string"}},
                    {"name": "VALUE", "datatype": {"base": "string"}}
                ],
                "primaryKey": ["ID"]
            }
        },
        {
            "url": "data/graphemes.tsv",
            "tableSchema": {
                "columns": [
                    {"name": "PK", "datatype": {"base": "integer"}},
                    {
                        "name": "GRAPHEME",
                        "dc:description":
                            "Grapheme used in a particular transcription to denote a sound",
                        "datatype": {"base": "string"}
                    },
                    {
                        "name": "NAME",
                        "dc:description":
                            "The ordered concatenation of feature values of the denoted sound",
                        "datatype": {"base": "string"}
                    },
                    {
                        "name": "BIPA",
                        "dc:description": "The grapheme for the denoted sound in the Broad IPA "
                                          "transcription system",
                        "datatype": {"base": "string"}
                    },
                    {"name": "DATASET", "dc:description": "Links to the source of this grapheme"},
                    {"name": "FREQUENCY", "datatype": {"base": "integer"}},
                    {
                        "name": "URL",
                        "dc:description": "URL of the grapheme in its source online database",
                        "datatype": {"base": "anyURI"}
                    },
                    {
                        "name": "IMAGE",
                        "dc:description": "Image of the typeset grapheme.",
                        "valueUrl":
                            "http://web.uvic.ca/ling/resources/ipa/charts/IPAlab/images/{IMAGE}",
                        "datatype": {"base": "anyURI"}
                    },
                    {
                        "name": "SOUND",
                        "dc:description": "Audio recording of the sound being pronounced.",
                        "valueUrl":
                            "http://web.uvic.ca/ling/resources/ipa/charts/IPAlab/IPAsounds/{SOUND}",
                        "datatype": {"base": "anyURI"}
                    },
                    {
                        "name": "EXPLICIT",
                        "dc:description":
                            "Indicates whether the mapping of grapheme to sound was done manually "
                            "(explicitly, +) or whether it was inferred from the Grapheme.",
                        "datatype": {"base": "string"}
                    },
                    {
                        "name": "FEATURES",
                        "dc:description": "Features of the sound as described in the local feature "
                                          "system of the source dataset",
                        "datatype": {"base": "string"}
                    },
                    {
                        "name": "NOTE",
                        "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#comment",
                        "datatype": {"base": "string"}
                    }
                ],
                "primaryKey": ["PK"],
                "foreignKeys": [
                    {
                        "columnReference": ["NAME"],
                        "reference": {
                            "columnReference": ["NAME"],
                            "resource": "data/sounds.tsv"
                        }
                    },
                    {
                        "columnReference": ["DATASET"],
                        "reference": {
                            "columnReference": ["NAME"],
                            "resource": "sources/index.tsv"
                        }
                    }
                ]
            }
        },
        {
            "url": "data/sounds.tsv",
            "tableSchema": {
                "columns": [
                    {
                        "name": "ID",
                        "valueUrl": "https://clts.clld.org/parameters/{ID}",
                        "datatype": {"base": "string"}
                    },
                    {
                        "name": "NAME",
                        "dc:description": "Ordered list of features + sound type",
                        "datatype": {"base": "string"}
                    },
                    {
                        "name": "FEATURES",
                        "dc:description": "Ordered list of feature values for the sound.",
                        "separator": " ",
                        "datatype": {"base": "string"}
                    },
                    {
                        "name": "GRAPHEME",
                        "dc:description": "CLTS choses the BIPA grapheme as canonical "
                                          "representative of the graphemes mapped to a sound.",
                        "datatype": {"base": "string"}
                    },
                    {
                        "name": "UNICODE",
                        "dc:description": "Unicode character names of the codepoints in GRAPHEME",
                        "separator": " / ",
                        "datatype": {"base": "string"}
                    },
                    {
                        "name": "GENERATED",
                        "dc:description":
                            "Indicates whether the sound was inferred by our algorithmic procedure "
                            "(which is active for all diphthongs, all cluster sounds, but also all "
                            "sounds which we do not label explicitly) or whether no inference was "
                            "needed, since the sound is explicitly defined.",
                        "datatype": {"base": "boolean", "format": "+|-"}},
                    {
                        "name": "TYPE",
                        "dc:description":
                            "CLTS defines five sound types: consonant, vowel, tone, diphthong, and "
                            "cluster. The latter two are always GENERATED.",
                        "datatype": {
                            "base": "string", "format": "consonant|vowel|diphthong|tone|cluster"}
                    },
                    {
                        "name": "NOTE",
                        "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#comment",
                        "datatype": {"base": "string"}
                    }
                ],
                "primaryKey": ["NAME"],
                "foreignKeys": [
                    {
                        "columnReference": ["FEATURES"],
                        "reference": {
                            "columnReference": ["ID"],
                            "resource": "data/features.tsv"
                        }
                    }
                ]
            }
        }
    ]
}


def register(parser):
    parser.add_argument(
        "--destination",
        default=None,
        type=PathType(type='file', must_exist=False),
        help="Name of the file to store data in compressed form."
    )


@attr.s
class Grapheme(object):
    GRAPHEME = attr.ib()
    NAME = attr.ib()
    EXPLICIT = attr.ib()
    DATASET = attr.ib()
    FREQUENCY = attr.ib(default=0)
    URL = attr.ib(default='')
    FEATURES = attr.ib(default='')
    IMAGE = attr.ib(default='')
    SOUND = attr.ib(default='')
    NOTE = attr.ib(default='')


def run(args):
    args.destination = args.destination or args.repos.path('data', 'clts.zip')

    def writer(*comps):
        return UnicodeWriter(args.repos.path('data', *comps), delimiter='\t')

    sounds = collections.defaultdict(dict)
    data = []
    clts_dump = collections.OrderedDict()
    bipa = args.repos.bipa
    # start from assembling bipa-sounds
    args.log.info('adding bipa data')
    for grapheme, sound in sorted(
        bipa.sounds.items(),
        key=lambda p: (p[1].alias if p[1].alias else False, p[0], p[1].uname)
    ):
        if sound.type not in ['marker']:
            if sound.alias:
                assert sound.name in sounds
                sounds[sound.name]['aliases'].add(grapheme)
            else:
                assert sound.name not in sounds
                sounds[sound.name] = {
                    'grapheme': grapheme,
                    'unicode': sound.uname or '',
                    'generated': '',
                    'note': sound.note or '',
                    'type': sound.type,
                    'aliases': set(),
                    'normalized': '+' if sound.normalized else '',
                    'sound': sound,
                }
            data.append(Grapheme(
                GRAPHEME=grapheme,
                NAME=sound.name,
                EXPLICIT='+',
                DATASET='bipa',
                NOTE=sound.note or ''))
            if grapheme not in clts_dump:
                clts_dump[grapheme] = [str(sound), sound.name]

    # add sounds systematically by their alias
    args.log.info('adding transcription data')
    for td in args.repos.iter_transcriptiondata():
        for name in td.names:
            bipa_sound = bipa[name]
            # check for consistency of mapping here
            if not is_valid_sound(bipa_sound, bipa):
                continue

            sound = sounds.get(name)
            if not sound:
                sound = sounds[name] = {
                    'grapheme': bipa_sound.s,
                    'aliases': {bipa_sound.s},
                    'generated': '+',
                    'unicode': bipa_sound.uname or '',
                    'note': '',
                    'type': bipa_sound.type,
                    'alias': '+' if bipa_sound.alias else '',
                    'normalized': '+' if bipa_sound.normalized else '',
                    'sound': bipa_sound,
                }

            for item in sorted(td.data[name], key=lambda d: (d['bipa_grapheme'], d['grapheme'])):
                sound['aliases'].add(item['grapheme'])
                # add the values here
                data.append(Grapheme(
                    GRAPHEME=item['grapheme'],
                    NAME=name,
                    EXPLICIT=item['explicit'],
                    DATASET=td.id,
                    FREQUENCY=item.get('frequency', ''),
                    URL=item.get('url', ''),
                    FEATURES=item.get('features', ''),
                    IMAGE=item.get('image', ''),
                    SOUND=item.get('sound', ''),
                ))
                if item['grapheme'] not in clts_dump:
                    clts_dump[item['grapheme']] = [sound['grapheme'], name]

    # sound classes have a generative component, so we need to treat them separately
    args.log.info('adding sound classes')
    for sc in args.repos.iter_soundclass():
        for name in sorted(sounds):
            try:
                grapheme = sc[name]
                data.append(Grapheme(
                    GRAPHEME=grapheme,
                    NAME=name,
                    EXPLICIT='+' if name in sc.data else '',
                    DATASET=sc.id,
                ))
            except KeyError:  # pragma: no cover
                args.log.debug(name, sounds[name]['grapheme'])

    # last run, check again for each of the remaining transcription systems,
    # whether we can translate the sound
    args.log.info('adding remaining transcription systems')
    for ts in args.repos.iter_transcriptionsystem(exclude=['bipa']):
        for name in sorted(sounds):
            try:
                ts_sound = ts[name]
                if is_valid_sound(ts_sound, ts):
                    sounds[name]['aliases'].add(ts_sound.s)
                    data.append(Grapheme(
                        GRAPHEME=ts_sound.s,
                        NAME=name,
                        EXPLICIT='' if sounds[name]['generated'] else '+',
                        DATASET=ts.id,
                    ))
                    if ts_sound.s not in clts_dump:
                        clts_dump[ts_sound.s] = [sounds[name]['grapheme'], name]
            except ValueError:
                pass
            except TypeError:  # pragma: no cover
                args.log.debug('{0}: {1}'.format(ts.id, name))

    counts = {
        'index.tsv': len(args.repos.meta),
        'features.tsv': 0,
        'graphemes.tsv': 0,
        'sounds.tsv': 0,
    }

    args.log.info('writing data to file')

    fids = set()
    with writer('features.tsv') as w:
        w.writerow(['ID', 'TYPE', 'FEATURE', 'VALUE'])
        for k, v in load(args.repos.pkg_dir / 'transcriptionsystems' / 'features.json').items():
            for f, vals in v.items():
                for val in vals:
                    fids.add('_'.join([k, f, val]))
                    w.writerow(['_'.join([k, f, val]), k, f, val])
                    counts['features.tsv'] += 1

    with writer('sounds.tsv') as w:
        w.writerow(['ID', 'NAME', 'FEATURES', 'TYPE', 'GRAPHEME', 'UNICODE', 'GENERATED', 'NOTE'])
        for k, v in sorted(sounds.items(), reverse=True):
            features = []
            sound = v['sound']
            if sound.type in ['vowel', 'consonant', 'tone']:
                csounds = [sound]
            else:
                csounds = [sound.from_sound, sound.to_sound]
            for sound in csounds:
                for kk, vv in sound.featuredict.items():
                    if vv:
                        fid = '{}_{}_{}'.format(sound.type, kk, vv)
                        if fid in fids:
                            features.append(fid)
                        else:
                            args.log.warning('illegal feature value: {}'.format(fid))

            w.writerow([
                k.replace(' ', '_'),
                k,
                ' '.join(features),
                v['type'],
                v['grapheme'],
                v['unicode'],
                v['generated'],
                v['note'],
            ])
            counts['sounds.tsv'] += 1

    with writer('graphemes.tsv') as w:
        w.writerow(['PK'] + [f.name for f in attr.fields(Grapheme)])
        for pk, row in enumerate(data, start=1):
            w.writerow([pk] + list(attr.astuple(row)))
            counts['graphemes.tsv'] += 1

    for table in METADATA['tables']:
        table['dc:extent'] = counts[table['url'].split('/')[-1]]

    METADATA.update(load(args.repos.repos / 'metadata.json'))
    md_path = args.repos.repos / 'cldf-metadata.json'
    dump(METADATA, md_path, indent=4)
    ds = Dataset.from_metadata(md_path)
    ds.validate(log=args.log)
    md = []
    for level, header, text in iter_markdown_sections(metadata2markdown(ds, md_path)):
        if level == 1:
            md.append(text)
        else:
            md.append('\n#' + header)
            md.append(text)

    upsert_section(args.repos.repos / 'README.md', 'CLDF Dataset', 2, '\n'.join(md))

    with zipfile.ZipFile(
        str(args.destination),
        mode='w',
        compression=zipfile.ZIP_DEFLATED
    ) as myzip:
        myzip.writestr('clts.json', json.dumps(clts_dump))
