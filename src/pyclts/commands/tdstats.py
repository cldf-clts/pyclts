"""
Stats on transcription data
"""
from pyclts.models import is_valid_sound
from clldutils.clilib import add_format, Table


def register(parser):
    add_format(parser, default='simple')


def run(args):
    with Table(args, 'id', 'valid', 'total', 'percent') as table:
        bipa = args.repos.bipa
        for td in args.repos.iter_transcriptiondata():
            ln = [1 if is_valid_sound(bipa[name], bipa) else 0 for name in td.names]
            table.append([td.id, sum(ln), len(ln), sum(ln) / len(ln)])
        table.append([
            len(table),
            '',
            '',
            0 if not len(table) else sum([line[-1] for line in table]) / (len(table))])
