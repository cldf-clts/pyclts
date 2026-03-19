import functools
import dataclasses
import unicodedata
from typing import Optional, TYPE_CHECKING, Any

from clldutils.misc import nfilter

from pyclts.util import norm, jaccard
from .features import ConsonantFeatures, VowelFeatures, ToneFeatures, Features

if TYPE_CHECKING:
    from pyclts.transcriptionsystem import TranscriptionSystem

__all__ = [
    'is_valid_sound',
    'Symbol', 'Sound', 'Consonant', 'Vowel', 'Tone', 'Marker',
    'Diphthong', 'Cluster', 'UnknownSound']


def is_valid_sound(sound: 'Symbol', ts: 'TranscriptionSystem') -> bool:
    """Check the consistency of a given transcription system conversion"""
    if isinstance(sound, (Marker, UnknownSound)):
        return False
    s1 = ts[sound.name]
    s2 = ts[sound.s]
    return s1.name == s2.name and s1.s == s2.s


@dataclasses.dataclass
class Symbol:
    """Any atomic part of text."""
    ts: 'TranscriptionSystem'
    grapheme: str
    source: Optional[str] = None
    generated: bool = False
    note: Optional[str] = None

    @functools.cached_property
    def type(self) -> str:  # pylint: disable=C0116
        return self.__class__.__name__.lower()

    def __str__(self) -> str:
        """A symbol is represented by its grapheme, i.e. the way it looks like in text."""
        return self.grapheme

    def __eq__(self, other):
        """
        In the absence of features, we consider symbols equal, if they belong to the same
        system and are represented by the same grapheme.
        """
        return self.ts.id == other.ts.id and self.grapheme == other.grapheme

    @property
    def name(self) -> None:  # pylint: disable=C0116
        return None

    @property
    def uname(self) -> str:
        "Return unicode name(s) for a character set."
        try:
            return ' / '.join(unicodedata.name(ss) for ss in str(self))
        except TypeError:
            return '-'
        except ValueError:
            return '?'

    @property
    def codepoints(self) -> str:
        "Return unicode codepoint(s) for a grapheme."
        return ' '.join('U+' + ('000' + hex(ord(x))[2:])[-4:] for x in str(self))


@dataclasses.dataclass
class UnknownSound(Symbol):
    """Marker for unknown stuff passed to systems for identification."""


@functools.cache
def fieldnames(cls) -> list[str]:
    """Fieldnames of a dataclass. Cached for performance."""
    return [f.name for f in dataclasses.fields(cls)]


@dataclasses.dataclass(eq=False, repr=False)
class Sound(Symbol):
    """
    Sound object stores basic features of the individual sound objects.
    """
    base: Optional[str] = None
    alias: Optional[str] = None
    normalized: Optional[str] = None
    unknown: Optional[str] = None
    stress: Optional[str] = None

    features = None

    @property
    def name_order(self):
        return self.features.name_order()

    def __getattr__(self, item):
        return getattr(self.features, item)

    @classmethod
    def from_kw(cls, **kw):
        fkw = {}
        fnames = fieldnames(cls.__annotations__['features'])
        for name in list(kw.keys()):
            if name in fnames:
                fkw[name] = kw.pop(name)
        kw['features'] = cls.__annotations__['features'](**fkw)
        return cls(**kw)

    def asdict(self) -> dict[str, Any]:
        """dataclasses.asdict is very slow, so we provide a simplistic alternative."""
        # FIXME: add feature data!
        res = {f: getattr(self, f) for f in fieldnames(self.__class__)}
        res.update({f: getattr(self.features, f) for f in fieldnames(self.__annotations__['features'])})
        return res

    def __eq__(self, other):
        if isinstance(other, Sound):
            return self.name == other.name
        return False

    def __repr__(self):
        return f'<{self.__module__}.{self.__class__.__name__}: {self.name}>'

    def __add__(self, other) -> str:
        """Concatenate graphemes."""
        return str(self) + str(other)

    def __hash__(self):
        """We want to use sounds as dict keys or in sets."""
        return hash(self.name)

    @property
    def s(self) -> str:
        """Shortcut."""
        return str(self)

    def _features(self) -> list[str]:
        return nfilter(getattr(self.features, p, None) for p in self.name_order)

    @property
    def featuredict(self) -> dict[str, Optional[str]]:
        """The feature values associated with a Symbol."""
        return {f: getattr(self.features, f, None) for f in self.name_order}

    @property
    def featureset(self) -> frozenset[str]:
        """The feature values associated with a Symbol suitable as dict key."""
        return frozenset(self._features() + [self.type])

    def similarity(self, other) -> float:
        """Compute the similarity of two symbols based on their features."""
        return jaccard(self.featureset, other.featureset)

    def _iter_normed_feature_values(self, features: list[str], base_vals):
        for feature in features:
            if feature not in base_vals and getattr(self.features, feature, '') in self._features():
                yield norm(self.ts.diacritics_grapheme_by_value[self.type].get(getattr(self.features, feature, ''), '<!>'))

    def __str__(self) -> str:
        """
        Return the reference representation of the sound.

        Note
        ----
        We first try to return the non-alias value in our data. If this fails,
        we create the sound based on it's feature representation.
        """
        # generated sounds need to be re-produced for double-checking
        if not self.generated:
            if not self.alias and self.grapheme in self.ts.sounds:
                return self.grapheme
            elif self.alias and self.featureset in self.ts.features_to_sound:
                return str(self.ts.features_to_sound[self.featureset])
            # this can usually not happen, as we catch these errors when loading a ts!
            raise ValueError(f'Orphaned alias {self.grapheme}')  # pragma: no cover

        # search for best base-string
        excluded = self.features.feature_values_excluded_in_str()
        elements = [f for f in self._features() if f not in excluded] + [self.type]
        base_str = self.base or '<?>'
        base_graphemes = []
        while elements:
            base = self.ts.features_to_sound.get(frozenset(elements))
            if base:
                base_graphemes.append(base.grapheme)
            elements.pop(0)
        base_str = base_graphemes[-1] if base_graphemes else base_str or '<?>'
        base_vals = {
            self.ts._feature_values[elm] for elm in
            self.ts.sounds[base_str].name.split(' ')[:-1]} if base_str != '<?>' else {}
        out: list[str] = []
        out.extend(self._iter_normed_feature_values(self.features.pre_order(), base_vals))
        out.append(base_str)
        out.extend(self._iter_normed_feature_values(self.features.post_order(), base_vals))
        return ''.join(out)

    @property
    def name(self):
        return ' '.join([f or '' for f in self._features()] + [self.type])

    @property
    def table(self):
        """Returns the tabular representation of the sound as given in our data
        """
        tbl = []
        features = [
            f for f in self.name_order if f not in self.ts.columns[self.type]]
        # make sure to mark generated sounds
        if self.generated and self.s != self.source:
            tbl += [str(self) + ' | ' + self.source]
        else:
            tbl += [str(self)]
        for name in self.ts.columns[self.type][1:]:
            if name != 'extra' and name != 'alias':
                tbl += [getattr(self, name) or '']
            elif name == 'alias':
                tbl += ['+' if getattr(self, name) else '']
            else:
                bundle = []
                for f in features:
                    val = getattr(self, f)
                    if val:
                        bundle += ['{0}:{1}'.format(f, val)]
                tbl += [','.join(bundle)]
        return tbl

    @property
    def symbols(self):
        """Returns all unicode sounds separated by the empty sound marker.
        """
        return ' '.join(['◌' + s for s in self.s])


@dataclasses.dataclass(eq=False)
class Marker(Symbol):
    alias: Optional[str] = None
    feature: Optional[str] = None
    value: Optional[str] = None
    unknown: Optional[str] = None
    features: Features = dataclasses.field(default_factory=Features)

    @classmethod
    def from_kw(cls, **kw):
        return cls(**kw)

    @property
    def name(self):
        return self.grapheme

    @property
    def featureset(self):
        return frozenset([self.grapheme, self.type])


@dataclasses.dataclass(eq=False, repr=False)
class Consonant(Sound):
    features: ConsonantFeatures = dataclasses.field(default_factory=ConsonantFeatures)


@dataclasses.dataclass(repr=False, eq=False)
class ComplexSound(Sound):
    from_sound: Optional[str] = None
    to_sound: Optional[str] = None
    features: Features = dataclasses.field(default_factory=Features)

    @staticmethod
    def match(sound1, sound2) -> bool:
        raise NotImplemented

    def __str__(self):
        return str(self.from_sound) + str(self.to_sound)

    @property
    def name(self):
        n1 = ' '.join(self.from_sound.name.split(' ')[:-1])
        n2 = ' '.join(self.to_sound.name.split(' ')[:-1])
        return 'from ' + n1 + ' to ' + n2 + ' ' + self.type

    def _features(self):
        res = ['from_' + p for p in nfilter(
            getattr(self.from_sound, p, None) for p in self.from_sound.name_order)]
        res.extend([
            'to_' + p for p in nfilter(
                getattr(self.to_sound, p, None) for p in self.to_sound.name_order)])
        if self.from_sound.type == "vowel":
            res.append("diphthong")
        if self.from_sound.type == "consonant":
            res.append("cluster")
        return res

    @property
    def featuredict(self):
        res = {'from_' + p: getattr(self.from_sound, p, None) for p in self.from_sound.name_order}
        res.update({'to_' + p: getattr(self.to_sound, p, None) for p in self.to_sound.name_order})
        return res

    @classmethod
    def from_sounds(cls, source, sound1, sound2, ts):
        return cls(
            source=source,
            grapheme=sound1.grapheme + sound2.grapheme,
            from_sound=sound1,
            to_sound=sound2,
            ts=ts,
            generated=True,
            stress=sound1.stress or sound2.stress
        )

    @property
    def table(self):
        """Overwrite the table attribute for complex sounds"""
        return [self.grapheme, self.from_sound.name, self.to_sound.name]


@dataclasses.dataclass(repr=False, eq=False)
class Cluster(ComplexSound):
    """
    A cluster of two consonants whose manner is either plosive or implosive.

    Notes
    -----
    To keep the search space low and to avoid that users start defining too
    invalid sound clusters, we restrict the ```manner``` attribute of the two
    sounds to ```plosive``` and ```implosive```.
    """
    features: Features = dataclasses.field(default_factory=Features)

    @staticmethod
    def match(sound1, sound2):
        if isinstance(sound1, Consonant):
            if \
             sound1.manner in sound1.validated('manner', 'stop', 'implosive', 'click', 'nasal') and\
             sound2.manner in sound2.validated('manner', 'stop', 'implosive', 'affricate'):
                return True

            if sound1.manner == 'click' and sound2.manner == 'fricative':
                return True
        return False


@dataclasses.dataclass(repr=False, eq=False)
class Vowel(Sound):
    features: VowelFeatures = dataclasses.field(default_factory=VowelFeatures)


@dataclasses.dataclass(repr=False, eq=False)
class Diphthong(ComplexSound):
    """
    A dipthong consists of two vowels.
    """
    features: Features = dataclasses.field(default_factory=Features)

    @staticmethod
    def match(sound1, _):
        return isinstance(sound1, Vowel)


@dataclasses.dataclass(repr=False, eq=False)
class Tone(Sound):
    features: ToneFeatures = dataclasses.field(default_factory=ToneFeatures)
