"""Auxiliary functions for pyclts."""
import re
import pathlib
import functools
import collections
from collections.abc import Iterable, Generator
import dataclasses
import unicodedata
from typing import Union, Literal, get_args, Optional, Any, TYPE_CHECKING

from csvw import Table
from csvw.dsv import reader

if TYPE_CHECKING:
    from pyclts.api import CLTS

__all__ = [
    'EMPTY', 'UNKNOWN', 'norm', 'nfd', 'jaccard', 'itertable', 'dict_reader', 'fieldnames']

EMPTY = "◌"
UNKNOWN = "�"
PathType = Union[str, pathlib.Path]
GraphemeMapType = dict[str, dict[str, str]]
DataType = dict[str, list[dict[str, str]]]
SoundsType = list[str]
NamesType = list[str]
MetadataType = dict[Literal['NAME', 'DESCRIPTION', 'REFS', 'TYPE', 'URITEMPLATE'], str]

dict_reader = functools.partial(reader, delimiter='\t', dicts=True)


@functools.cache
def fieldnames(cls) -> list[str]:
    """Fieldnames of a dataclass. Cached for performance."""
    return [f.name for f in dataclasses.fields(cls)]


def normalize_whitespace(s: str) -> str:
    """Replace clusters of whitespace with a single space."""
    return re.sub(r'\s+', ' ', s.strip().replace('\n', ' '))


@dataclasses.dataclass(frozen=True)
class CLDFTable:
    """
    A base class for data objects which are to be serialized as rows in tables of the CLDF dataset.

    The specification of the columns (i.e. the dataclass fields) are also used to create a CLDF
    specification of the table metadata.
    """
    __dialect__ = {"commentPrefix": None, "delimiter": "\t", "trim": True}
    _row_ids = []

    @classmethod
    def primary_key(cls) -> Optional[str]:
        """Primary keys in CLDF tables are typically marked as CLDF id property."""
        for f in dataclasses.fields(cls):
            if f.metadata.get('propertyUrl') == 'http://cldf.clld.org/v1.0/terms.rdf#id':
                return f.name
        return None  # pragma: no cover

    @classmethod
    def cldf_table_spec(cls) -> dict[str, Any]:
        """CLDF metadata suitable for serialization as JSON."""
        res = {
            "url": cls.rel_path(),
            "dc:description": normalize_whitespace(cls.__doc__) if cls.__doc__ else '',
            "tableSchema": {
                "columns": [cls.cldf_column_spec(field) for field in dataclasses.fields(cls)],
            }
        }
        pk = cls.primary_key()
        if pk:
            res["tableSchema"]["primaryKey"] = [pk]
        fks = {f.name: f.metadata['fk'] for f in dataclasses.fields(cls) if f.metadata.get('fk')}
        if fks:
            res["tableSchema"]["foreignKeys"] = [
                {
                    "columnReference": [colref],
                    "reference": {"columnReference": [fk.primary_key()], "resource": fk.rel_path()}
                } for colref, fk in fks.items()]
        return res

    @classmethod
    def cldf_column_spec(cls, field) -> dict[str, Any]:
        """CLDF metadata suitable for serialization as JSON."""
        res = {"name": field.name}
        res['datatype'] = {"base": "string"}
        annotation = cls.__annotations__[field.name]
        if annotation == int:
            res['datatype'] = {"base": "integer"}
        if type(annotation) is type(Literal['']):
            res['datatype'] = {
                "base": "string",
                "format": "|".join(re.escape(arg) for arg in get_args(annotation))}
        res.update({k: v for k, v in field.metadata.items() if k != 'fk'})
        return res

    @classmethod
    def rel_path(cls) -> str:
        """The path of the table's TSV file relative to the metadata location."""
        return NotImplemented  # pragma: no cover

    @classmethod
    def path_in_repos(cls, api: 'CLTS') -> pathlib.Path:
        """The table's path in the repository."""
        return api.repos / cls.rel_path()

    @classmethod
    def iter_rows(
            cls, api: 'CLTS', _  # pylint: disable=W0613
    ) -> Generator[list[str], None, None]:
        """Called from write method."""
        yield []  # pragma: no cover

    @classmethod
    def write(cls, api: 'CLTS', objs=None):
        """Write the table data using the CLDF metadata."""
        spec = cls.cldf_table_spec()
        spec['dialect'] = cls.__dialect__
        table = Table.fromvalue(spec)
        pk = cls.primary_key()
        rows = list(cls.iter_rows(api, objs))
        if pk:
            pk = fieldnames(cls).index(pk)
            for row in rows:
                cls._row_ids.append(row[pk])
        table.write(rows, cls.path_in_repos(api))
        return len(rows)

    @classmethod
    def row_ids(cls) -> list[str]:
        """After the table has been written, the primary keys of the rows can be accessed."""
        return cls._row_ids


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
