"""Auxiliary functions for pyclts."""

import unicodedata
from collections import defaultdict
from pathlib import Path

from csvw.dsv import reader

__all__ = ['EMPTY', 'UNKNOWN', 'norm', 'nfd', 'TranscriptionBase']

EMPTY = "◌"
UNKNOWN = "�"


class TranscriptionBase(object):
    __type__ = None

    def __init__(self, path, system=None):
        self.path = Path(path)
        self.system = system

    @property
    def id(self):
        return self.path.stem

    def resolve_sound(self, sound):
        raise NotImplementedError  # pragma: no cover

    def __getitem__(self, sound):
        """Return a Sound instance matching the specification."""
        return self.resolve_sound(sound)

    def get(self, sound, default=None):
        try:
            res = self[sound]
            if getattr(res, 'type', None) == 'unknownsound' and default:
                return default
            return res
        except KeyError:
            return default

    def __call__(self, sounds, default="0"):
        return [self.get(x, default=default) for x in sounds.split()]

    def translate(self, string, target_system):
        return ' '.join('{0}'.format(
            target_system.get(self[s].name or '?', '?')) for s in string.split())


def norm(string):
    return string.replace(EMPTY, "")


def nfd(string):
    return unicodedata.normalize("NFD", string)


def itertable(table):
    """Auxiliary function for iterating over a data table."""
    for item in table:
        res = {
            k.lower(): nfd(v) if isinstance(v, str) else v for k, v in item.items()}
        for extra in res.pop('extra', None) or []:
            k, _, v = extra.partition(':')
            res[k.strip()] = v.strip()
        yield res


def read_data(fname, grapheme_col, *cols):
    grapheme_map, data, sounds, names = {}, defaultdict(list), [], []

    for row in reader(fname, delimiter='\t', dicts=True):
        grapheme_map[row[grapheme_col]] = row['BIPA_GRAPHEME']
        grapheme = {"grapheme": row[grapheme_col]}
        for col in cols:
            grapheme[col.lower()] = row[col]
        data[row['BIPA_GRAPHEME']].append(grapheme)
        data[row['CLTS_NAME']].append(grapheme)
        sounds.append(row['BIPA_GRAPHEME'])
        names.append(row['CLTS_NAME'])

    return grapheme_map, data, sounds, names
