"""

"""
from pyclts.cli_util import add_format, Table


def register(parser):
    add_format(parser, default='simple')
    parser.add_argument(
        '--type',
        help='CLTS data type',
        choices=['sc', 'ts', 'td'],
        default='ts')


def run(args):
    with Table(args, 'id', 'description', 'refs', 'type', 'uritemplate') as table:
        for src in args.repos.meta:
            if src['TYPE'] == args.type:
                table.append(src.values())
