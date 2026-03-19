#
# FIXME: We need a mechanism, a function or similar to make sure the implementation is compatible
# with the data in the repos, namely pkg/transcriptionsystems/features.json
#
import functools
import dataclasses
from typing import Literal, get_args

EXCLUDE_FEATURES = [  # FIXME: compute from metadata!
    'apical',
    'laminal',  # laminality
    'ejective',  # ejection
    'with-falling_tone',  # tone
    'with-extra-low_tone',
    'with-extra-high_tone',
    'with-falling_tone',
    'with-low_tone',
    'with-global_fall',
    'with-global_rise',
    'with-high_tone',
    'with-mid_tone',
    'with-rising_tone',
    'with-upstep'
]


@functools.cache
def fields(cls):
    return dataclasses.fields(cls)


@dataclasses.dataclass(frozen=True)
class Features:
    """Base class for feature implementations."""
    def __post_init__(self):
        for field in self.fields():
            value = getattr(self, field.name)
            if value:
                if value not in self.valid_values()[field.name]:
                    raise ValueError(
                        f'Invalid {self.__class__.__name__}:{field.name} value {value}')

    @classmethod
    @functools.lru_cache(maxsize=3)  # Maxsize should be the number of subclasses.
    def fields(cls):
        return fields(cls)

    @classmethod
    @functools.lru_cache(maxsize=3)
    def valid_values(cls) -> dict[str, tuple[str]]:
        return {field.name: get_args(cls.__annotations__[field.name]) for field in cls.fields()}

    def validated(self, feature, *vals):
        assert all(val in  self.__class__.valid_values()[feature] for val in vals)
        return vals

    @classmethod
    @functools.lru_cache(maxsize=3)
    def name_order(cls):
        """The order of features used for composing the name of a sound."""
        return [f.name for f in cls.fields()]

    @classmethod
    def _order(cls, name):
        """
        Write order determines how sounds are written according to their features. This normalizes
        the order of diacritics preceding and following the base part of the sound.

        Fields can specify an index as value of metadata fields "pre" or "post".
        """
        fields = (f for f in cls.fields() if name in f.metadata)
        return [f.name for f in sorted(fields, key=lambda f_: f_.metadata[name])]

    @classmethod
    @functools.lru_cache(maxsize=3)
    def post_order(cls):
        """Features or their markers appearing after the base part of a symbol."""
        return cls._order('post')

    @classmethod
    @functools.lru_cache(maxsize=3)
    def pre_order(cls):
        """Features or their markers appearing before the base part of a symbol."""
        return cls._order('pre')


@dataclasses.dataclass(frozen=True)
class ConsonantFeatures(Features):
    raising: Literal[
        "lowered", "raised"
    ] = dataclasses.field(default=None, metadata={'post': 1})
    relative_articulation: Literal[
        "centralized", "mid-centralized", "advanced", "retracted"
    ] = dataclasses.field(default=None, metadata={'post': 2})
    friction: Literal[
        "with-friction"
    ] = dataclasses.field(default=None, metadata={'post': 20})
    articulation: Literal[
        "strong", "weak"
    ] = dataclasses.field(default=None, metadata={'post': 10})
    preceding: Literal[
        "pre-aspirated", "pre-breathy-aspirated", "pre-glottalized", "pre-labialized",
        "pre-nasalized", "pre-palatalized", "pre-glottalized-and-nasalized"
    ] = dataclasses.field(default=None, metadata={'pre': 1})
    syllabicity: Literal[
        "syllabic"
    ] = dataclasses.field(default=None, metadata={'post': 8})
    nasalization: Literal[
        "nasalized"
    ] = dataclasses.field(default=None, metadata={'post': 11})
    palatalization: Literal[
        "labio-palatalized", "palatalized"
    ] = dataclasses.field(default=None, metadata={'post': 13})
    labialization: Literal[
        "labialized"
    ] = dataclasses.field(default=None, metadata={'post': 14})
    velarization: Literal[
        "velarized"
    ] = dataclasses.field(default=None, metadata={'post': 15})
    pharyngealization: Literal[
        "pharyngealized"
    ] = dataclasses.field(default=None, metadata={'post': 16})
    glottalization: Literal[
        "glottalized"
    ] = dataclasses.field(default=None, metadata={'post': 17})
    aspiration: Literal[
        "aspirated"
    ] = dataclasses.field(default=None, metadata={'post': 19})
    duration: Literal[
        "long", "ultra-long", "mid-long"
    ] = dataclasses.field(default=None, metadata={'post': 21})
    release: Literal[
        "unreleased", "with-lateral-release", "with-mid-central-vowel-release",
        "with-nasal-release", "with-uvular-release", "with-sibilant-release",
        "with-trilled-release"
    ] = dataclasses.field(default=None, metadata={'post': 12})
    voicing: Literal[
        "devoiced", "revoiced"
    ] = dataclasses.field(default=None, metadata={'post': 9})
    creakiness: Literal[
        "creaky"
    ] = dataclasses.field(default=None, metadata={'post': 4})
    breathiness: Literal[
        "breathy"
    ] = dataclasses.field(default=None, metadata={'post': 18})
    phonation: Literal[
        "voiced", "voiceless", "unspecified-voice"
    ] = dataclasses.field(default=None, metadata={'post': 6})
    laminality: Literal[
        "apical", "laminal"
    ] = dataclasses.field(default=None, metadata={'post': 3, 'exclude': True})
    tongue_root: Literal[
        "advanced-tongue-root", "retracted-tongue-root"
    ] = dataclasses.field(default=None, metadata={'post': 5})
    place: Literal[
        "alveolar", "alveolo-palatal", "bilabial", "dental", "epiglottal", "glottal", "labial",
        "linguolabial", "labio-palatal", "labio-velar", "labio-dental", "palatal", "palatal-velar",
        "pharyngeal", "post-alveolar", "retroflex", "uvular", "velar", "bilabial-and-alveolar",
        "bilabial-and-velar", "alveolar-and-bilabial", "alveolar-and-velar", "velar-and-alveolar",
        "velar-and-bilabial", "velar-and-uvular", "unspecified-place"
    ] = None
    ejection: Literal[
        "ejective"
    ] = dataclasses.field(default=None, metadata={'post': 7, 'exclude': True})
    airstream: Literal[
        "sibilant", "whistled-sibilant", "lateral"
    ] = None
    manner: Literal[
        "affricate", "approximant", "click", "fricative", "implosive", "nasal", "nasal-click",
        "stop", "tap", "trill", "unspecified-manner"
    ] = None


@dataclasses.dataclass(frozen=True)
class VowelFeatures(Features):
    duration: Literal[
        "long", "mid-long", "ultra-long", "ultra-short"
    ] = dataclasses.field(default=None, metadata={'post': 18})
    rhotacization: Literal[
        "rhotacized"
    ] = dataclasses.field(default=None, metadata={'post': 14})
    pharyngealization: Literal[
        "pharyngealized"
    ] = dataclasses.field(default=None, metadata={'post': 15})
    glottalization: Literal[
        "glottalized"
    ] = dataclasses.field(default=None, metadata={'post': 16})
    velarization: Literal[
        "velarized"
    ] = dataclasses.field(default=None, metadata={'post': 17})
    syllabicity: Literal[
        "non-syllabic"
    ] = dataclasses.field(default=None, metadata={'post': 8})
    relative_articulation: Literal[
        "centralized", "mid-centralized", "advanced", "retracted"
    ] = dataclasses.field(default=None, metadata={'post': 10})
    tongue_root: Literal[
        "advanced-tongue-root", "retracted-tongue-root"
    ] = dataclasses.field(default=None, metadata={'post': 1})
    raising: Literal[
        "lowered", "raised"
    ] = dataclasses.field(default=None, metadata={'post': 2})
    rounding: Literal[
        "less-rounded", "more-rounded"
    ] = dataclasses.field(default=None, metadata={'post': 4})
    articulation: Literal[
        "strong", "weak"
    ] = dataclasses.field(default=None, metadata={'post': 13})
    nasalization: Literal[
        "nasalized"
    ] = dataclasses.field(default=None, metadata={'post': 11})
    voicing: Literal[
        "devoiced"
    ] = dataclasses.field(default=None, metadata={'post': 5})
    creakiness: Literal[
        "creaky"
    ] = dataclasses.field(default=None, metadata={'post': 7})
    breathiness: Literal[
        "breathy"
    ] = dataclasses.field(default=None, metadata={'post': 6})
    roundedness: Literal[
        "rounded", "unrounded"
    ] = None
    height: Literal[
        "close", "close-mid", "mid", "near-close", "near-open", "open", "open-mid"
    ] = None
    friction: Literal[
        "with-friction"
    ] = dataclasses.field(default=None, metadata={'post': 9})
    centrality: Literal[
        "back", "central", "front", "near-back", "near-front"
    ] = dataclasses.field(default=None, metadata={'post': 3})
    tone: Literal[
        "with-downstep", "with-extra-high_tone", "with-extra-low_tone", "with-falling_tone",
        "with-global_fall", "with-global_rise", "with-high_tone", "with-low_tone", "with-mid_tone",
        "with-rising_tone", "with-upstep"
    ] = dataclasses.field(default=None, metadata={'post': 12, 'exclude': True})


@dataclasses.dataclass(frozen=True)
class ToneFeatures(Features):
    contour: Literal[
        "contour", "falling", "flat", "rising", "short"] = None
    start: Literal[
        "from-high", "from-low", "from-mid", "from-mid-high", "from-mid-low", "neutral"] = None
    middle: Literal[
        "via-high", "via-low", "via-mid", "via-mid-high", "via-mid-low"] = None
    end: Literal[
        "to-high", "to-low", "to-mid", "to-mid-high", "to-mid-low"] = None
