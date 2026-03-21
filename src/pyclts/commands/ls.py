"""
List systems of a pyrticular type.
"""
from typing import get_args

from clldutils.clilib import add_format, Table

from pyclts.datatypes import DatatypeNameType, TranscriptionSystem


def register(parser):  # pylint: disable=C0116
    add_format(parser, default='simple')
    parser.add_argument(
        '--type',
        help='CLTS data type',
        choices=get_args(DatatypeNameType),
        default=TranscriptionSystem.type())


def run(args):  # pylint: disable=C0116
    with Table(args, 'id', 'description', 'refs', 'type', 'uritemplate') as table:
        for src in args.repos.meta:
            if src['TYPE'] == args.type:
                table.append(src.values())
