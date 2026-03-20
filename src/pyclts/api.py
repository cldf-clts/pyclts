"""
Access CLTS data programmatically.
"""
import functools
from typing import Optional
from collections.abc import Generator

from clldutils.apilib import API
from clldutils.misc import nfilter
from cldfcatalog import Config
from pybtex.database import parse_string

from pyclts.transcriptiondata import TranscriptionData
from pyclts.transcriptionsystem import TranscriptionSystem
from pyclts.soundclasses import SoundClasses
from pyclts.soundclasses import SOUNDCLASS_SYSTEMS
from pyclts.util import PathType, dict_reader, MetadataType


class CLTS(API):
    """The API for CLTS data."""
    def __init__(self, repos: PathType = None):
        if repos is None:
            repos = Config.from_file().get_clone('clts')  # pragma: no cover
        super().__init__(repos)
        self.pkg_dir = self.repos / 'pkg'
        self.transcriptionsystems_dir = self.pkg_dir / 'transcriptionsystems'
        self.transcriptiondata_dir = self.pkg_dir / 'transcriptiondata'
        self.soundclasses_dir = self.pkg_dir / 'soundclasses'

    @functools.cached_property
    def bipa(self) -> TranscriptionSystem:  # pylint: disable=C0116
        return self.transcriptionsystem('bipa')

    @functools.cached_property
    def meta(self) -> list[MetadataType]:  # pylint: disable=C0116
        res = list(dict_reader(self.repos / 'sources' / 'index.tsv'))
        for src in res:
            src['REFS'] = nfilter([s.strip() for s in src['REFS'].split(',')])
        return res

    @functools.cached_property
    def references(self):  # pylint: disable=C0116
        return parse_string(
            self.path('data', 'references.bib').read_text(encoding='utf8'), 'bibtex').entries

    def get_meta(self, obj) -> Optional[MetadataType]:  # pylint: disable=C0116
        for src in self.meta:
            if obj.__type__ == src['TYPE'] and obj.id == src['NAME']:
                return src
        return None

    def iter_sources(  # pylint: disable=C0116
            self,
            type=None,  # pylint: disable=W0622
    ) -> Generator[tuple[dict[str, str], list[dict[str, str]]], None, None]:
        for src in self.meta:
            if (type is None) or (type == src['TYPE']):
                graphemesp = self.repos / 'sources' / src['NAME'] / 'graphemes.tsv'
                if graphemesp.exists():
                    yield src, list(dict_reader(graphemesp))

    def get_source(self, name) -> Optional[list[dict[str, str]]]:
        """Get data from a source of transcription data, reading its graphemes table."""
        graphemesp = self.repos / 'sources' / name / 'graphemes.tsv'
        if graphemesp.exists():
            return list(dict_reader(graphemesp))
        return None  # pragma: no cover

    def iter_transcriptiondata(  # pylint: disable=C0116
            self) -> Generator[TranscriptionData, None, None]:
        for td in sorted(self.transcriptiondata_dir.iterdir(), key=lambda p: p.name):
            if td.suffix == '.tsv':
                yield TranscriptionData(td, self.bipa)

    def iter_soundclass(self) -> Generator[SoundClasses, None, None]:  # pylint: disable=C0116
        for sc in SOUNDCLASS_SYSTEMS:
            yield SoundClasses(self.soundclasses_dir / 'lingpy.tsv', self.bipa, sc)

    def iter_transcriptionsystem(  # pylint: disable=C0116
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
    def transcriptionsystem_dict(self) -> dict[str, TranscriptionSystem]:  # pylint: disable=C0116
        return {ts.id: ts for ts in self.iter_transcriptionsystem()}

    def transcriptionsystem(self, key) -> TranscriptionSystem:  # pylint: disable=C0116
        if key in self.transcriptionsystem_dict:
            return self.transcriptionsystem_dict[key]
        return TranscriptionSystem(
            key, self.transcriptionsystems_dir / 'transcription-system-metadata.json')

    @functools.cached_property
    def transcriptiondata_dict(self) -> dict[str, TranscriptionData]:  # pylint: disable=C0116
        return {ts.id: ts for ts in self.iter_transcriptiondata()}

    def transcriptiondata(self, key) -> TranscriptionData:  # pylint: disable=C0116
        if key in self.transcriptiondata_dict:
            return self.transcriptiondata_dict[key]
        return TranscriptionData(key, self.bipa)

    @functools.cached_property
    def soundclasses_dict(self) -> dict[str, SoundClasses]:  # pylint: disable=C0116
        return {ts.id: ts for ts in self.iter_soundclass()}

    def soundclass(self, key) -> SoundClasses:  # pylint: disable=C0116
        return self.soundclasses_dict[key]
