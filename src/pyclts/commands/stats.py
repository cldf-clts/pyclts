"""
Compute summary stats.
"""
import collections

from clldutils.clilib import add_format, Table

from pyclts.util import dict_reader


def register(parser):  # pylint: disable=C0116
    add_format(parser, default='pipe')


def run(args):  # pylint: disable=C0116
    sounds = {row['NAME']: row for row in dict_reader(args.repos.path('data', 'sounds.tsv'))}
    graphs = {
        '{GRAPHEME}-{NAME}-{DATASET}'.format(**row): row  # pylint: disable=C0209
        for row in dict_reader(args.repos.path('data', 'graphemes.tsv'))}

    graphdict = collections.defaultdict(list)
    for _, row in graphs.items():
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
