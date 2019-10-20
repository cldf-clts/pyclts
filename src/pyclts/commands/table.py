"""

"""
import collections

from pyclts.cli_util import Table, add_format


def register(parser):
    add_format(parser)
    parser.add_argument(
        '--filter',
        choices=['generated', 'unknown', 'known'],
        help='',
        default=None)
    parser.add_argument(
        'sounds',
        metavar='SOUNDS',
        nargs='+',
        help='sounds to display info for')


def run(args):
    tts = args.repos.transcriptionsystem(args.system)
    tts_sounds = [
        tts.get(sound if isinstance(sound, str) else sound.decode('utf8')) for sound in args.sounds]

    if args.filter == 'generated':
        tts_sounds = [s for s in tts_sounds if s.generated]
    elif args.filter == 'unknown':
        tts_sounds = [s for s in tts_sounds if s.type == 'unknownsound']
    elif args.filter == 'known':
        tts_sounds = [s for s in tts_sounds if not s.generated and not s.type == 'unknownsound']

    data = collections.defaultdict(list)
    ucount = 0
    for sound in tts_sounds:
        if sound.type != 'unknownsound':
            data[sound.type] += [sound.table]
        else:
            ucount += 1
            data['unknownsound'].append([str(ucount), sound.source or '', sound.grapheme])
    for cls in tts.sound_classes:
        if cls in data:
            print('# {0}\n'.format(cls))
            with Table(args, *[c.upper() for c in tts.columns[cls]]) as table:
                table.extend(data[cls])
            print('')
    if data['unknownsound']:
        print('# Unknown sounds\n')
        with Table(args, 'NUMBER', 'SOURCE', 'GRAPHEME') as table:
            table.extend(data['unknownsound'])
