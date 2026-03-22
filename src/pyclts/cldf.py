import dataclasses
from collections.abc import Generator
from typing import get_args, Optional

from clldutils.jsonlib import load

from pyclts.models import BaseSoundclassType, Vowel, Consonant, Tone, SoundclassNameType
from pyclts.util import CLDFTable
from pyclts.metadata import Source

__all__ = ['FeatureTable']


@dataclasses.dataclass(frozen=True)
class FeatureTable(CLDFTable):
    """
    The feature system employed by CLTS describes sounds by assigning values for certain features
    (constrained by sound type). The permissible values per (feature, sound type) are listed in
    this table.
    """
    ID: str = dataclasses.field(
        metadata={"propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id"}
    )
    TYPE: BaseSoundclassType = dataclasses.field(
        metadata={
            "dc:description":
                "CLTS distinguishes the basic sound types consonant, vowel, tone, and "
                "marker. Features are defined for consonants, vowels, and tones."}
    )
    FEATURE: str = dataclasses.field(
        metadata={"dc:description": "Note that CLTS features are not necessarily binary."}
    )
    VALUE: str = dataclasses.field(
        metadata={}
    )

    @classmethod
    def rel_path(cls):
        return 'data/features.tsv'

    @classmethod
    def iter_rows(cls, api, fids) -> Generator[list[str], None, None]:
        """
        Write features.tsv, yielding row IDs.
        """
        features_in_repos = load(api.pkg_dir / 'transcriptionsystems' / 'features.json')
        assert set(features_in_repos) == set(get_args(BaseSoundclassType))

        features_in_pyclts = {
            type_.type(): type_.__annotations__['features'].valid_values()
            for type_ in [Vowel, Consonant, Tone]}

        for type_, vv in features_in_repos.items():
            if 'stress' in vv:
                del vv['stress']  # stress is not really a feature and treated separately in pyclts.
            repos = set(vv)
            pyclts = set(features_in_pyclts[type_])
            assert pyclts == repos, \
                f'{type_}: pkg - repo: {pyclts - repos}; repo - pkg: {repos - pyclts}'
            for fname, values in vv.items():
                repos = set(values)
                pyclts = set(features_in_pyclts[type_][fname])
                assert pyclts == repos, \
                    (f'{type_}:{fname}: pkg - repo: {pyclts - repos}; repo - pkg: {repos - pyclts}')
                for val in values:
                    row = [type_, fname, val]
                    fids.add('_'.join(row))
                    yield ['_'.join(row)] + row


@dataclasses.dataclass(frozen=True)
class SoundTable(CLDFTable):
    ID: str = dataclasses.field(
        metadata={"valueUrl": "https://clts.clld.org/parameters/{ID}"}
    )
    NAME: str = dataclasses.field(
        metadata={"dc:description": "Ordered list of features + sound type",
                  "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id"}
    )
    FEATURES: list[str] = dataclasses.field(
        metadata={
            "dc:description": "Ordered list of feature values for the sound.",
            "separator": " ",
            "fk": FeatureTable}
    )
    TYPE: SoundclassNameType = dataclasses.field(
        metadata={
            "dc:description":
                "CLTS defines five sound types: consonant, vowel, tone, diphthong, and "
                "cluster. The latter two are always GENERATED."}
    )
    GRAPHEME: str = dataclasses.field(
        metadata={
            "dc:description":
                "CLTS choses the BIPA grapheme as canonical "
                "representative of the graphemes mapped to a sound."}
    )
    UNICODE: list[str] = dataclasses.field(
        metadata={
            "dc:description":
                "Unicode character names of the codepoints in GRAPHEME",
            "separator": " / "}
    )
    GENERATED: Optional[str] = dataclasses.field(
        metadata={
            "dc:description":
                "Indicates whether the sound was inferred by our algorithmic procedure "
                "(which is active for all diphthongs, all cluster sounds, but also all "
                "sounds which we do not label explicitly) or whether no inference was "
                "needed, since the sound is explicitly defined.",
            "datatype": {"base": "boolean", "format": "+|-"}}
    )
    NOTE: str = dataclasses.field(
        default='',
        metadata={"propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#comment"}
    )

    @staticmethod
    def _get_features(sound, fids, log):
        features = []
        if isinstance(sound, (Vowel, Consonant, Tone)):
            csounds = [sound]
        else:
            csounds = [sound.from_sound, sound.to_sound]
        for sound in csounds:
            for kk, vv in sound.featuredict.items():
                if vv:
                    fid = f'{sound.type()}_{kk}_{vv}'
                    if fid in fids:
                        features.append(fid)
                    else:
                        log.warning('illegal feature value: %s', fid)  # pragma: no cover
        return features

    @classmethod
    def from_grapheme_and_sound(cls, grapheme, sound, fids, log):
        """
        """
        return cls(
            ID=sound.name.replace(' ', '_'),
            NAME=sound.name,
            FEATURES=cls._get_features(sound, fids, log),
            GRAPHEME=grapheme,
            UNICODE=(sound.uname or '').split(' / '),
            GENERATED=None,
            NOTE=sound.note or '',
            TYPE=sound.type())

    @classmethod
    def from_name_and_sound(cls, name, sound, fids, log):
        return cls(
            ID=name.replace(' ', '_'),
            NAME=name,
            FEATURES=cls._get_features(sound, fids, log),
            GRAPHEME=sound.s,
            GENERATED='+',
            UNICODE=(sound.uname or '').split(' / '),
            TYPE=sound.type())

    @classmethod
    def rel_path(cls):
        return 'data/sounds.tsv'

    @classmethod
    def iter_rows(cls, api, sounds):
        for sound in sounds:
            yield dataclasses.astuple(sound)


@dataclasses.dataclass(frozen=True)
class GraphemeTable(CLDFTable):
    PK: str = dataclasses.field(metadata={
        "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id"})
    GRAPHEME: str = dataclasses.field(metadata={
        "dc:description": "Grapheme used in a particular transcription to denote a sound"})
    NAME: str = dataclasses.field(metadata={
        "fk": SoundTable,
        "dc:description": "The ordered concatenation of feature values of the denoted sound"})
    EXPLICIT: str = dataclasses.field(metadata={
        "dc:description":
            "Indicates whether the mapping of grapheme to sound was done manually "
            "(explicitly, +) or whether it was inferred from the Grapheme."})
    DATASET: str = dataclasses.field(metadata={
        "fk": Source, "dc:description": "Links to the source of this grapheme"})
    FREQUENCY: int = dataclasses.field(default=0, metadata={})
    URL: str = dataclasses.field(
        default='',
        metadata={"dc:description": "URL of the grapheme in its source online database"})
    FEATURES: str = dataclasses.field(
        default='',
        metadata={
            "dc:description": "Features of the sound as described in the local feature "
                              "system of the source dataset"})
    IMAGE: str = dataclasses.field(
        default='',
        metadata={
            "dc:description": "Image of the typeset grapheme.",
            "valueUrl": "http://web.uvic.ca/ling/resources/ipa/charts/IPAlab/images/{IMAGE}"})
    SOUND: str = dataclasses.field(
        default='',
        metadata={
            "dc:description": "Audio recording of the sound being pronounced.",
            "valueUrl": "http://web.uvic.ca/ling/resources/ipa/charts/IPAlab/IPAsounds/{SOUND}"})
    NOTE: str = dataclasses.field(
        default='',
        metadata={"propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#comment"}
    )

    @classmethod
    def rel_path(cls):
        return "data/graphemes.tsv"

    @classmethod
    def iter_rows(cls, api, graphemes):
        for grapheme in graphemes:
            yield dataclasses.astuple(grapheme)
