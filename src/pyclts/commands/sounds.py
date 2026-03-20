"""
Display basic info about sounds
"""
from clldutils.clilib import add_format, Table

from pyclts.cli_util import add_sounds


def register(parser):  # pylint: disable=C0116
    add_format(parser)
    add_sounds(parser)


def run(args):  # pylint: disable=C0116
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
