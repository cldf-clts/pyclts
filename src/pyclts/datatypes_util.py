"""
Base class for "systems", i.e. systematic collections of data about aspects of transcriptions.
"""
import pathlib
import functools
import dataclasses
from typing import get_args, Literal
from collections.abc import Generator

from csvw import Table

from .util import PathType, itertable, EMPTY
from .models import UnknownSound, Sound, BaseSoundclassType, BaseSoundclassMappingType


class TranscriptionBase:
    """Functionality based on data read from files."""
    __type__ = None

    def __init__(self, path: PathType, system=None):
        self.path = pathlib.Path(path)
        self.system = system

    @classmethod
    @functools.lru_cache(maxsize=5)
    def type(cls) -> str:
        """We want to have the lowercased class name handy for dict keys, etc."""
        return ''.join(c.lower() for c in cls.__name__ if c.isupper())

    @property
    def id(self) -> str:
        """The directory/file name identifies the transcription."""
        return self.path.stem

    def resolve_sound(self, sound) -> Sound:
        """Abstract method"""
        raise NotImplementedError  # pragma: no cover

    def __getitem__(self, sound):
        """Return a Sound instance matching the specification."""
        return self.resolve_sound(sound)

    def get(self, sound, default=None):
        """Imitates dict.get, i.e. __getitem__ with default."""
        try:
            res = self[sound]
            if isinstance(res, UnknownSound) and default:
                return default
            return res
        except KeyError:
            return default

    def __call__(self, sounds, default="0") -> list:
        if isinstance(sounds, str):
            sounds = sounds.split()

        return [self.get(x, default=default) for x in sounds]

    def translate(self, string: str, target_system: dict[str, str]):
        """Translate symbols from one system to another."""
        return ' '.join(f"{target_system.get(self[s].name or '?', '?')}" for s in string.split())


@dataclasses.dataclass(frozen=True)
class Diacritics:
    """Lookup tables for a system's diacritics."""
    grapheme_by_value: BaseSoundclassMappingType = dataclasses.field(
        default_factory=lambda: {sc: {} for sc in get_args(BaseSoundclassType)})
    value_by_grapheme: BaseSoundclassMappingType = dataclasses.field(
        default_factory=lambda: {sc: {} for sc in get_args(BaseSoundclassType)})

    @classmethod
    def from_table(cls, table: Table, feature_values):
        """Initialize the lookup tables from the data in the system's diacritics file."""
        res = cls()
        for dia in itertable(table):
            if not dia['alias'] and not dia['typography']:
                res.grapheme_by_value[dia['type']][dia['value']] = dia['grapheme']
            # assign feature values to the dictionary
            feature_values[dia['value']] = dia['feature']
            res.value_by_grapheme[dia['type']][dia['grapheme']] = dia['value']
        return res


@dataclasses.dataclass
class SymbolWithDiacritics:
    """
    Components of a symbol decorated with left- and right-attaching diacritics for easier
    processing.
    """
    pre: str = ''
    base: str = ''
    post: str = ''

    def iter_add_pre(
            self,
            diacritics: Diacritics,
            base_sound: Sound,
            grapheme: list[str],
            sound: list[str],
    ) -> Generator[str, None, None]:
        """Add left-attaching diacritics to sound and grapheme, yielding new features."""
        yield from self._add('pre', diacritics, base_sound, grapheme, sound)

    def iter_add_post(
            self,
            diacritics: Diacritics,
            base_sound: Sound,
            grapheme: list[str],
            sound: list[str],
    ) -> Generator[str, None, None]:
        """Add right-attaching diacritics to sound and grapheme, yielding new features."""
        yield from self._add('post', diacritics, base_sound, grapheme, sound)

    def _add(  # pylint: disable=R0913,R0917
            self, what: Literal['pre', 'post'], diacritics, base_sound, grapheme, sound):
        dias = [EMPTY + p for p in self.post] if what == 'post' else [p + EMPTY for p in self.pre]
        index = 1 if what == 'post' else 0
        for dia in dias:
            feature = diacritics.value_by_grapheme[base_sound.type()].get(dia, {})
            if not feature:
                raise ValueError(dia)
            yield feature
            grapheme.append(dia[index])
            sound.append(diacritics.grapheme_by_value[base_sound.type()][feature][index])
