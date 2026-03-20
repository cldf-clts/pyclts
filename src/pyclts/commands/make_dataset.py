"""
Prepare transcriptiondata from the transcription sources.
"""
from csvw.dsv import UnicodeWriter

from pyclts.cli_util import get_processed_transcription_data


def register(parser):  # pylint: disable=C0116
    parser.add_argument("dataset", help="the dataset")


def run(args):  # pylint: disable=C0116
    def writer(*comps):
        return UnicodeWriter(args.repos.path('pkg', *comps), delimiter='\t')

    columns = ['LATEX', 'FEATURES', 'SOUND', 'IMAGE', 'COUNT', 'NOTE']
    bipa = args.repos.bipa
    rows = args.repos.get_source(args.dataset)
    src = [s for s in args.repos.meta if s['NAME'] == args.dataset][0]
    out = get_processed_transcription_data(src, rows, columns, bipa, args.log)

    with writer('transcriptiondata', f'{args.dataset}.tsv') as w:
        w.writerows(out)
