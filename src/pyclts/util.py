"""Auxiliary functions for pyclts."""
import pathlib
import functools
import collections
from collections.abc import Iterable, Generator
import unicodedata
from typing import Union

from clldutils.markup import iter_markdown_sections
from csvw import Table
from csvw.dsv import reader

__all__ = [
    'EMPTY', 'UNKNOWN', 'norm', 'nfd', 'TranscriptionBase', 'jaccard', 'upsert_section',
    'itertable', 'dict_reader']

EMPTY = "◌"
UNKNOWN = "�"
PathType = Union[str, pathlib.Path]
GraphemeMapType = dict[str, dict[str, str]]
DataType = dict[str, list[dict[str, str]]]
SoundsType = list[str]
NamesType = list[str]

dict_reader = functools.partial(reader, delimiter='\t', dicts=True)


class TranscriptionBase:
    """Functionality based on data read from files."""
    __type__ = None

    def __init__(self, path: PathType, system=None):
        self.path = pathlib.Path(path)
        self.system = system

    @property
    def id(self) -> str:
        """The directory/file name identifies the transcription."""
        return self.path.stem

    def resolve_sound(self, sound):
        """Abstract method"""
        raise NotImplementedError  # pragma: no cover

    def __getitem__(self, sound):
        """Return a Sound instance matching the specification."""
        return self.resolve_sound(sound)

    def get(self, sound, default=None):
        """Imitates dict.get, i.e. __getitem__ with default."""
        try:
            res = self[sound]
            if getattr(res, 'type', None) == 'unknownsound' and default:
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


def norm(string: str) -> str:
    """Strip empty markers."""
    return string.replace(EMPTY, "")


def nfd(string: str) -> str:
    """Apply unicode normalization."""
    return unicodedata.normalize("NFD", string)


def itertable(table: Table) -> Generator[dict[str, str]]:
    """Auxiliary function for iterating over a data table."""
    for item in table:
        res = {
            k.lower(): nfd(v) if isinstance(v, str) else v for k, v in item.items()}
        for extra in res.pop('extra', None) or []:
            k, _, v = extra.partition(':')
            res[k.strip()] = v.strip()
        yield res


def read_data(
        fname: PathType,
        grapheme_col: str,
        *cols: Iterable[str],
) -> tuple[GraphemeMapType, DataType, SoundsType, NamesType]:
    """Read data from a TSV file."""
    grapheme_map, data, sounds, names = {}, collections.defaultdict(list), [], []

    for row in dict_reader(fname):
        grapheme_map[nfd(row[grapheme_col])] = row['BIPA_GRAPHEME']
        grapheme = {"grapheme": row[grapheme_col]}
        for col in cols:
            grapheme[col.lower()] = row[col]
        data[row['BIPA_GRAPHEME']].append(grapheme)
        data[row['CLTS_NAME']].append(grapheme)
        sounds.append(row['BIPA_GRAPHEME'])
        names.append(row['CLTS_NAME'])

    return grapheme_map, data, sounds, names


def jaccard(a: Union[set, frozenset], b: Union[set, frozenset]) -> float:
    """Compute the Jaccard distance. See https://en.wikipedia.org/wiki/Jaccard_index"""
    i, u = len(a.intersection(b)), len(a.union(b))
    return i / u if u else 0


def upsert_section(p: pathlib.Path, in_header: str, level: int, new: str):
    """Upsert a section in a markdown formatted file."""
    res, found, in_section = [], False, False
    for clevel, header, text in iter_markdown_sections(p.read_text(encoding='utf8')):
        if in_section:
            if clevel > level:
                continue
            in_section = False
        if clevel == level and in_header in header:
            text, found, in_section = new, True, True
        res.extend([header, text or ''])
    if not found:
        res.extend([f"\n\n{level * '#'} {in_header}\n\n", new + '\n'])
    p.write_text(''.join(t or '' for t in res), encoding='utf8')
