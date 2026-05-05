"""
List the elements of the feature system.
"""
from clldutils.clilib import add_format, Table

from pyclts.models import Marker, UnknownSound


def register(parser):  # pylint: disable=C0116
    add_format(parser, default='pipe')


def run(args):  # pylint: disable=C0116
    ts = args.repos.transcriptionsystem(args.system)
    features = set()
    for sound in ts.sounds.values():
        if not isinstance(sound, (Marker, UnknownSound)):
            for k, v in sound.featuredict.items():
                features.add((sound.type(), k, v or ''))
    with Table(args, 'TYPE', 'FEATURE', 'VALUE') as table:
        table.extend(sorted(features))
