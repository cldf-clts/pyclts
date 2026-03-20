"""Auxiliary functions for pyclts."""
import pathlib
import functools
import collections
from collections.abc import Iterable, Generator
import unicodedata
from typing import Union, Literal

from csvw import Table
from csvw.dsv import reader

__all__ = ['EMPTY', 'UNKNOWN', 'norm', 'nfd', 'jaccard', 'itertable', 'dict_reader', 'MetadataType']

EMPTY = "◌"
UNKNOWN = "�"
PathType = Union[str, pathlib.Path]
GraphemeMapType = dict[str, dict[str, str]]
DataType = dict[str, list[dict[str, str]]]
SoundsType = list[str]
NamesType = list[str]
MetadataType = dict[Literal['NAME', 'DESCRIPTION', 'REFS', 'TYPE', 'URITEMPLATE'], str]

dict_reader = functools.partial(reader, delimiter='\t', dicts=True)


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
