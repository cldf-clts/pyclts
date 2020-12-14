"""
Prepare transcriptiondata from the transcription sources.
"""
from pyclts.models import is_valid_sound


def register(parser):
    parser.add_argument("dataset", help="the dataset")


def run(args):
    bipa = args.repos.bipa
    rows = args.repos.get_source(args.dataset)
    graphemes = {}
    errors = []
    for i, row in enumerate(rows):
        if row['GRAPHEME'] in graphemes:
            if row['BIPA'] == graphemes[row['GRAPHEME']]:
                args.log.info('duplicate grapheme in the data: {0}'.format(row['GRAPHEME']))
            else:
                args.log.warn('duplicate grapheme «{0}» has BIPA «{1}» and «{2}»'.format(
                    row['GRAPHEME'],
                    row['BIPA'],
                    graphemes[row['GRAPHEME']]))
                errors += [(i + 1, row['BIPA'], row['GRAPHEME'])]

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
        elif explicit and bipa_sound.type == 'marker':
            pass
        elif explicit and bipa_sound.type == 'unknownsound':
            args.log.error('unknown sound encountered for BIPA «{0}» (Line {1})'.format(
                row['BIPA'],
                i + 1))
            errors += [(i + 1, row['BIPA'], row['GRAPHEME'])]
        elif explicit and not is_valid_sound(bipa_sound, bipa):
            args.log.error('invalid BIPA «{0}» (Line {1})'.format(
                row['BIPA'],
                i + 1))
            errors += [(i + 1, row['BIPA'], row['GRAPHEME'])]
    if not errors:
        args.log.info('No errors found in the data')
    else:
        args.log.info('Found {0} errors in the data.'.format(len(errors)))
