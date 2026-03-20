"""
Stats on transcription data
"""
from clldutils.clilib import add_format, Table

from pyclts.models import is_valid_sound


def register(parser):  # pylint: disable=C0116
    add_format(parser, default='simple')


def run(args):  # pylint: disable=C0116
    with Table(args, 'id', 'valid', 'total', 'percent') as table:
        bipa = args.repos.bipa
        for td in args.repos.iter_transcriptiondata():
            ln = [1 if is_valid_sound(bipa[name], bipa) else 0 for name in td.names]
            table.append([td.id, sum(ln), len(ln), sum(ln) / len(ln)])
        total = sum(line[-1] for line in table) if table else 0
        table.append([len(table), '', '', total / len(table)])
