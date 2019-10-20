"""

"""
import collections

from csvw.dsv import reader

from pyclts.cli_util import add_format, Table


def register(parser):
    add_format(parser)


def run(args):
    def read(fname):
        return reader(args.repos.path('data', fname), delimiter='\t', dicts=True)

    sounds = {row['NAME']: row for row in read('sounds.tsv')}
    graphs = {'{GRAPHEME}-{NAME}-{DATASET}'.format(**row): row for row in read('graphemes.tsv')}

    graphdict = collections.defaultdict(list)
    for id_, row in graphs.items():
        graphdict[row['GRAPHEME']].append(row['DATASET'])

    with Table(args, 'DATA', 'STATS', 'PERC') as text:
        text.append(
            ['Unique graphemes', len(set(row['GRAPHEME'] for row in graphs.values())), ''])
        text.append(['different sounds', len(sounds), ''])
        text.append(
            ['singletons', len([g for g in graphdict if len(set(graphdict[g])) == 1]), ''])
        text.append(
            ['multiples', len([g for g in graphdict if len(set(graphdict[g])) > 1]), ''])
        total = len(sounds)
        for type_, count in collections.Counter([s['TYPE'] for s in sounds.values()]).most_common():
            text.append([type_ + 's', count, count / total])
