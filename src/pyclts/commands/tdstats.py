"""
Stats on transcription data
"""
from clldutils.markup import Table

from pyclts.models import is_valid_sound
from pyclts.cli_util import add_format


def register(parser):
    add_format(parser, default='simple')


def run(args):
    table = Table('id', 'valid', 'total', 'percent')
    bipa = args.repos.bipa
    for td in args.repos.iter_transcriptiondata():
        ln = [1 if is_valid_sound(bipa[name], bipa) else 0 for name in td.names]
        table.append([td.id, sum(ln), len(ln), sum(ln) / len(ln)])
    table.append([
        len(table) - 1,
        '',
        '',
        0 if not len(table) - 1 else sum([line[-1] for line in table[1:]]) / (len(table) - 1)])
    print(table.render(tablefmt=args.format))
