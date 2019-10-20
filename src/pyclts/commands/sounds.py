"""
Display basic info about sounds
"""
from pyclts.cli_util import add_format, Table


def register(parser):
    add_format(parser)
    parser.add_argument(
        'sounds',
        metavar='SOUNDS',
        nargs='+',
        help='sounds to display info for')


def run(args):
    tts = args.repos.transcriptionsystem(args.system)
    with Table(args, args.system.upper(), 'SOURCE', 'GENERATED', 'ALIAS', 'NAME') as data:
        for sound in args.sounds:
            sound = tts.get(sound if isinstance(sound, str) else sound.decode('utf8'))
            if sound.type != 'unknownsound':
                data.append([
                    str(sound),
                    sound.source or ' ',
                    '1' if sound.generated else ' ',
                    sound.grapheme if sound.alias else ' ',
                    sound.name,
                ])
            else:
                data.append(['?', sound.source, '?', '?', '?'])
