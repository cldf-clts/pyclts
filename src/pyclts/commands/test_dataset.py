"""
Prepare transcriptiondata from the transcription sources.
"""
import logging
from collections.abc import Generator

from pyclts.models import Marker, UnknownSound


def register(parser):  # pylint: disable=C0116
    parser.add_argument("dataset", help="the dataset")


def run(args):  # pylint: disable=C0116
    bipa = args.repos.bipa
    rows = args.repos.get_source(args.dataset)
    graphemes = {}
    errors = []
    for row in enumerate(rows, start=1):
        errors.extend(list(_test_row(row, graphemes, bipa, args.log)))
    if not errors:
        args.log.info('No errors found in the data')
    else:
        args.log.warning('Found %s errors in the data.', len(errors))


def _test_row(
        row: tuple[int, dict[str, str]],
        graphemes,
        bipa,
        log: logging.Logger,
) -> Generator[tuple[int, str, str]]:
    i, row = row
    if row['GRAPHEME'] in graphemes:
        if row['BIPA'] == graphemes[row['GRAPHEME']]:
            log.info('duplicate grapheme in the data: %s', row['GRAPHEME'])
        else:
            log.warning(
                'duplicate grapheme «%s» has BIPA «%s» and «%s»',
                row['GRAPHEME'],
                row['BIPA'],
                graphemes[row['GRAPHEME']])
            yield (i, row['BIPA'], row['GRAPHEME'])

    graphemes[row['GRAPHEME']] = row['BIPA']
    explicit = False
    if not row['BIPA']:
        bipa_sound = bipa[row['GRAPHEME']]
    elif row['BIPA'] == '<NA>':
        bipa_sound = '<NA>'
        explicit = True
    else:
        bipa_sound = bipa[row['BIPA']]
        explicit = True

    if explicit and str(bipa_sound) == '<NA>':
        pass
    elif explicit and isinstance(bipa_sound, Marker):
        pass  # pragma: no cover
    elif explicit and isinstance(bipa_sound, UnknownSound):
        log.error('unknown sound encountered for BIPA «%s» (Line %s)', row['BIPA'], i)
        yield (i, row['BIPA'], row['GRAPHEME'])
    elif explicit and not bipa.is_valid(bipa_sound):  # pragma: no cover
        log.error('invalid BIPA «%s» (Line %s)', row['BIPA'], i)
        yield (i, row['BIPA'], row['GRAPHEME'])
