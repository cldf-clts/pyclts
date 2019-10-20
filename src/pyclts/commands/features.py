"""

"""
from pyclts.cli_util import add_format, Table


def register(parser):
    add_format(parser)


def run(args):
    ts = args.repos.transcriptionsystem(args.system)
    features = set()
    for sound in ts.sounds.values():
        if sound.type not in ['marker', 'unknownsound']:
            for k, v in sound.featuredict.items():
                features.add((sound.type, k, v or ''))
    with Table(args, 'TYPE', 'FEATURE', 'VALUE') as table:
        table.extend(sorted(features))
