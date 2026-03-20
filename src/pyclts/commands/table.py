"""
List sounds (possibly filtered) from a transcription system.
"""
import collections

from clldutils.clilib import Table, add_format

from pyclts.models import UnknownSound
from pyclts.cli_util import add_sounds


def register(parser):  # pylint: disable=C0116
    add_format(parser)
    add_sounds(parser)
    parser.add_argument(
        '--filter',
        choices=['generated', 'unknown', 'known'],
        help='',
        default=None)


def run(args):  # pylint: disable=C0116
    tts = args.repos.transcriptionsystem(args.system)
    tts_sounds = [
        tts.get(sound if isinstance(sound, str) else sound.decode('utf8')) for sound in args.sounds]

    if args.filter == 'generated':
        tts_sounds = [s for s in tts_sounds if s.generated]
    elif args.filter == 'unknown':
        tts_sounds = [s for s in tts_sounds if isinstance(s, UnknownSound)]
    elif args.filter == 'known':
        tts_sounds = [s for s in tts_sounds if not s.generated and not isinstance(s, UnknownSound)]

    data = collections.defaultdict(list)
    ucount = 0
    for sound in tts_sounds:
        if not isinstance(sound, UnknownSound):
            data[sound.type()].append(sound.table)
        else:
            ucount += 1
            data['unknownsound'].append([str(ucount), sound.source or '', sound.grapheme])

    for cls in tts.sound_classes:
        if cls in data:
            print(f'# {cls}\n')
            with Table(args, *[c.upper() for c in tts.columns[cls]]) as table:
                table.extend(data[cls])
            print('')

    if data['unknownsound']:
        print('# Unknown sounds\n')
        with Table(args, 'NUMBER', 'SOURCE', 'GRAPHEME') as table:
            table.extend(data['unknownsound'])
