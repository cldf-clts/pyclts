import functools
from typing import Optional
from collections.abc import Generator

from clldutils.apilib import API
from clldutils.misc import nfilter
from csvw.dsv import reader
from cldfcatalog import Config
from pybtex.database import parse_string

from pyclts import TranscriptionData, TranscriptionSystem, SoundClasses
from pyclts.soundclasses import SOUNDCLASS_SYSTEMS
from pyclts.util import PathType


def _rows(p):
    return list(reader(p, delimiter='\t', dicts=True))


class CLTS(API):
    def __init__(self, repos: PathType = None):
        if repos is None:
            repos = Config.from_file().get_clone('clts')  # pragma: no cover
        super().__init__(repos)
        self.pkg_dir = self.repos / 'pkg'
        self.transcriptionsystems_dir = self.pkg_dir / 'transcriptionsystems'
        self.transcriptiondata_dir = self.pkg_dir / 'transcriptiondata'
        self.soundclasses_dir = self.pkg_dir / 'soundclasses'

    @functools.cached_property
    def bipa(self) -> TranscriptionSystem:
        return self.transcriptionsystem('bipa')

    @functools.cached_property
    def meta(self) -> list[dict[str, str]]:
        res = _rows(self.repos / 'sources' / 'index.tsv')
        for src in res:
            src['REFS'] = nfilter([s.strip() for s in src['REFS'].split(',')])
        return res

    @functools.cached_property
    def references(self):
        return parse_string(
            self.path('data', 'references.bib').read_text(encoding='utf8'), 'bibtex').entries

    def get_meta(self, obj) -> Optional[dict[str, str]]:
        for src in self.meta:
            if obj.__type__ == src['TYPE'] and obj.id == src['NAME']:
                return src
        return None

    def iter_sources(
            self,
            type=None,
    ) -> Generator[tuple[dict[str, str], list[dict[str, str]]], None, None]:
        for src in self.meta:
            if (type is None) or (type == src['TYPE']):
                graphemesp = self.repos / 'sources' / src['NAME'] / 'graphemes.tsv'
                if graphemesp.exists():
                    yield src, _rows(graphemesp)

    def get_source(self, name) -> Optional[list[dict[str, str]]]:
        graphemesp = self.repos / 'sources' / name / 'graphemes.tsv'
        if graphemesp.exists():
            return _rows(graphemesp)

    def iter_transcriptiondata(self) -> Generator[TranscriptionData, None, None]:
        for td in sorted(self.transcriptiondata_dir.iterdir(), key=lambda p: p.name):
            if td.suffix == '.tsv':
                yield TranscriptionData(td, self.bipa)

    def iter_soundclass(self) -> Generator[SoundClasses, None, None]:
        for sc in SOUNDCLASS_SYSTEMS:
            yield SoundClasses(self.soundclasses_dir / 'lingpy.tsv', self.bipa, sc)

    def iter_transcriptionsystem(
            self,
            include_private=False,
            exclude=None,
    ) -> Generator[TranscriptionSystem, None, None]:
        exclude = exclude or []
        for ts in sorted(self.transcriptionsystems_dir.iterdir(), key=lambda p: p.name):
            if ts.is_dir():
                if (not ts.name.startswith('_')) or include_private:
                    if ts.name not in exclude:
                        yield TranscriptionSystem(
                            ts,
                            self.transcriptionsystems_dir / 'transcription-system-metadata.json')

    @functools.cached_property
    def transcriptionsystem_dict(self) -> dict[str, TranscriptionSystem]:
        return {ts.id: ts for ts in self.iter_transcriptionsystem()}

    def transcriptionsystem(self, key) -> TranscriptionSystem:
        if key in self.transcriptionsystem_dict:
            return self.transcriptionsystem_dict[key]
        return TranscriptionSystem(
            key, self.transcriptionsystems_dir / 'transcription-system-metadata.json')

    @functools.cached_property
    def transcriptiondata_dict(self) -> dict[str, TranscriptionData]:
        return {ts.id: ts for ts in self.iter_transcriptiondata()}

    def transcriptiondata(self, key) -> TranscriptionData:
        if key in self.transcriptiondata_dict:
            return self.transcriptiondata_dict[key]
        return TranscriptionData(key, self.bipa)

    @functools.cached_property
    def soundclasses_dict(self) -> dict[str, SoundClasses]:
        return {ts.id: ts for ts in self.iter_soundclass()}

    def soundclass(self, key) -> SoundClasses:
        return self.soundclasses_dict[key]
