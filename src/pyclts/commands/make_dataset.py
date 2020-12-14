"""
Prepare transcriptiondata from the transcription sources.
"""
from uritemplate import URITemplate
from csvw.dsv import UnicodeWriter
from pyclts.models import is_valid_sound


def process_transcription_data(rows, columns, src, uritemplate, bipa, args):
    out = [[
        'BIPA_GRAPHEME', 'CLTS_NAME', 'GENERATED', 'EXPLICIT', 'GRAPHEME',
        'SYMBOLS', 'URL'] + columns]
    graphemes = set()
    for row in rows:
        if row['GRAPHEME'] in graphemes:
            args.log.warn('skipping duplicate grapheme: {0}'.format(row['GRAPHEME']))
            continue
        graphemes.add(row['GRAPHEME'])
        if not row['BIPA']:
            bipa_sound = bipa[row['GRAPHEME']]
            explicit = ''
        else:
            bipa_sound = bipa[row['BIPA']]
            explicit = '+'
        generated = '+' if bipa_sound.generated else ''
        if not explicit:
            if is_valid_sound(bipa_sound, bipa):
                bipa_grapheme = bipa_sound.s
                bipa_name = bipa_sound.name
                bipa_symbols = bipa_sound.symbols
            else:
                bipa_grapheme, bipa_name, bipa_symbols = 3 * ['<NA>']
        else:
            if row['BIPA'] == '<NA>':
                bipa_grapheme, bipa_name, bipa_symbols = 3 * ['<NA>']
            elif bipa_sound.type == 'unknownsound':
                raise ValueError('wrong BIPA sound «{0}» in mapping'.format(
                    row['BIPA']))
            elif bipa_sound.type != 'marker' and not is_valid_sound(
                    bipa_sound,
                    bipa):
                raise ValueError('invalid BIPA sound «{0}» in mapping'.format(
                    row['BIPA']))
            elif bipa_sound.type == 'marker':
                bipa_grapheme, bipa_name, bipa_symbols = str(bipa_sound), '', ''
            else:
                bipa_grapheme, bipa_name, bipa_symbols = (
                    str(bipa_sound), bipa_sound.name, bipa_sound.symbols)
        url = uritemplate.expand(**row) if uritemplate else row.get('URL', '')
        out.append(
            [
                bipa_grapheme, bipa_name, generated, explicit, row['GRAPHEME'],
                bipa_symbols,
                url] + [
                    row.get(c, '') for c in columns])
    return out


def register(parser):
    parser.add_argument("dataset", help="the dataset")


def run(args):
    def writer(*comps):
        return UnicodeWriter(args.repos.path('pkg', *comps), delimiter='\t')

    columns = ['LATEX', 'FEATURES', 'SOUND', 'IMAGE', 'COUNT', 'NOTE']
    bipa = args.repos.bipa
    rows = args.repos.get_source(args.dataset)
    src = [src for src in args.repos.meta if src['NAME'] == args.dataset][0]
    uritemplate = URITemplate(src['URITEMPLATE']) if src['URITEMPLATE'] else None
    out = process_transcription_data(
        rows, columns, src, uritemplate, bipa,
        args)
    found = len([o for o in out if o[0] != '<NA>'])
    args.log.info('... {0} of {1} graphemes found ({2:.0f}%)'.format(
        found, len(out), found / len(out) * 100))
    with writer('transcriptiondata', '{0}.tsv'.format(args.dataset)) as w:
        w.writerows(out)
