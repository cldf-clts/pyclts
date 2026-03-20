"""
Utilities used in pyclts commands.
"""
import logging
from math import isnan
from typing import Optional
from collections.abc import Generator

from uritemplate import URITemplate

from pyclts.transcriptionsystem import TranscriptionSystem
from pyclts.models import is_valid_sound, UnknownSound, Marker
from pyclts.util import MetadataType

__all__ = ['add_sounds', 'get_processed_transcription_data']


def add_sounds(parser):
    """Add arguments to specify sounds."""
    parser.add_argument('sounds', metavar='SOUNDS', nargs='+', help='sounds to display info for')


def _iter_transcription_data(
        rows: list[dict[str, str]],
        columns: list[str],
        uritemplate: Optional[URITemplate],
        bipa: TranscriptionSystem,
        log: logging.Logger,
) -> Generator[list[str], None, None]:
    yield 'BIPA_GRAPHEME CLTS_NAME GENERATED EXPLICIT GRAPHEME SYMBOLS URL'.split() + columns
    graphemes = set()
    for row in rows:
        if row['GRAPHEME'] in graphemes:
            log.warning('skipping duplicate grapheme: %s', row['GRAPHEME'])
            continue
        graphemes.add(row['GRAPHEME'])
        bipa_sound = bipa[row['BIPA'] or row['GRAPHEME']]
        explicit = '+' if row['BIPA'] else ''
        generated = '+' if bipa_sound.generated else ''
        if not explicit:
            if is_valid_sound(bipa_sound, bipa):
                bipa_grapheme = bipa_sound.s
                bipa_name = bipa_sound.name
                bipa_symbols = bipa_sound.symbols
            else:
                bipa_grapheme, bipa_name, bipa_symbols = 3 * ['<NA>']
        else:
            if row['BIPA'] == '<NA>':
                bipa_grapheme, bipa_name, bipa_symbols = 3 * ['<NA>']
            elif isinstance(bipa_sound, UnknownSound):
                raise ValueError(
                    f"wrong BIPA sound «{row['BIPA']}» in mapping")  # pragma: no cover
            elif not isinstance(bipa_sound, Marker) and not is_valid_sound(bipa_sound, bipa):
                raise ValueError(
                    f"invalid BIPA sound «{row['BIPA']}» in mapping")  # pragma: no cover
            elif isinstance(bipa_sound, Marker):
                bipa_grapheme, bipa_name, bipa_symbols = str(bipa_sound), '', ''
            else:
                bipa_grapheme, bipa_name, bipa_symbols = (
                    str(bipa_sound), bipa_sound.name, bipa_sound.symbols)
        url = uritemplate.expand(**row) if uritemplate else row.get('URL', '')
        lrow = [bipa_grapheme, bipa_name, generated, explicit, row['GRAPHEME'], bipa_symbols, url]
        yield lrow + [row.get(c, '') for c in columns]


def get_processed_transcription_data(
        src: MetadataType,
        rows: list[dict[str, str]],
        columns: list[str],
        bipa: TranscriptionSystem,
        log: logging.Logger,
):
    """Process transcription data and return it as table rows."""
    uritemplate = URITemplate(src['URITEMPLATE']) if src['URITEMPLATE'] else None
    out = list(_iter_transcription_data(rows, columns, uritemplate, bipa, log))
    found = len([o for o in out if o[0] != '<NA>'])
    log.info('... %s of %s graphemes found (%.0f%%)', found, len(out), found / len(out) * 100)
    return out
