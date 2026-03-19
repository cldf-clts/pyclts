#
# FIXME: We need a mechanism, a function or similar to make sure the implementation is compatible
# with the data in the repos, namely pkg/transcriptionsystems/features.json
#
import functools
import dataclasses
import itertools
from typing import Literal, get_args, Union, Optional
from collections.abc import Generator

__all__ = ['Features', 'ConsonantFeatures', 'VowelFeatures', 'ToneFeatures']

# We cache some feature metadata per subclass of `Features`, using `functools.lru_cache`.
N_SUBCLASSES = 4


@dataclasses.dataclass(frozen=True)
class Features:
    """Base class for feature implementations."""
    def __post_init__(self):
        # Since Features instances are frozen, we can check the validity of the attribute values
        # once at instantiation.
        for field in self.fields():
            value = getattr(self, field.name)
            if value:
                if value not in self.valid_values()[field.name]:
                    raise ValueError(
                        f'Invalid {self.__class__.__name__}:{field.name} value {value}')

    @classmethod
    @functools.lru_cache(maxsize=N_SUBCLASSES)  # Maxsize should be the number of subclasses.
    def fields(cls):
        """The fields of the class."""
        return dataclasses.fields(cls)

    @classmethod
    @functools.lru_cache(maxsize=N_SUBCLASSES)
    def valid_values(cls) -> dict[str, tuple[str]]:
        """The feature system, i.e. all feature names with all valid values."""
        return {field.name: get_args(cls.__annotations__[field.name]) for field in cls.fields()}

    @classmethod
    @functools.lru_cache(maxsize=N_SUBCLASSES)
    def feature_values_excluded_in_str(cls) -> list[str]:
        """All feature values which should not appear in the string representation of a sound."""
        return list(itertools.chain.from_iterable(
            cls.valid_values()[f.name] for f in cls.fields() if f.metadata.get('exclude')))

    def validated(self, feature: str, *vals: str) -> Union[str, tuple[str]]:
        """
        Makes sure, values listed in `vals` are valid for feature `feature`.

        Returns a single string if just one value was passed, a tuple of all values otherwise.
        """
        assert all(val in  self.__class__.valid_values()[feature] for val in vals)
        return vals[0] if len(vals) == 1 else vals

    def __iter__(self) -> Generator[tuple[str, Optional[str]], None, None]:
        """Yield (feature name, value) pairs in name_order()."""
        for f in self.fields():
            yield f.name, getattr(self, f.name)

    @classmethod
    def _order(cls, name):
        """
        Write order determines how sounds are written according to their features. This normalizes
        the order of diacritics preceding and following the base part of the sound.

        Fields can specify an index as value of metadata fields "pre" or "post".
        """
        fields_ = (f for f in cls.fields() if name in f.metadata)
        return [f.name for f in sorted(fields_, key=lambda f_: f_.metadata[name])]

    @classmethod
    @functools.lru_cache(maxsize=N_SUBCLASSES)
    def post_order(cls):
        """Features or their markers appearing after the base part of a symbol."""
        return cls._order('post')

    @classmethod
    @functools.lru_cache(maxsize=N_SUBCLASSES)
    def pre_order(cls):
        """Features or their markers appearing before the base part of a symbol."""
        return cls._order('pre')


@dataclasses.dataclass(frozen=True)
class ConsonantFeatures(Features):  # pylint: disable=R0902,C0115
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
class VowelFeatures(Features):  # pylint: disable=R0902,C0115
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
    """Features of a tone."""
    contour: Literal[
        "contour", "falling", "flat", "rising", "short"] = None
    start: Literal[
        "from-high", "from-low", "from-mid", "from-mid-high", "from-mid-low", "neutral"] = None
    middle: Literal[
        "via-high", "via-low", "via-mid", "via-mid-high", "via-mid-low"] = None
    end: Literal[
        "to-high", "to-low", "to-mid", "to-mid-high", "to-mid-low"] = None
