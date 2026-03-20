"""
Called as part of the CLDF creation workflow.
"""
from clldutils.clilib import ParserError
from csvw.dsv import UnicodeWriter

from pyclts.cli_util import get_processed_transcription_data
from pyclts.soundclasses import SOUNDCLASS_SYSTEMS

try:
    from lingpy.sequence.sound_classes import token2class
    from lingpy.data import Model
    LINGPY = True
except ImportError:  # pragma: no cover
    LINGPY = False
    token2class = None
    Model = None


def run(args):  # pylint: disable=C0116
    if not LINGPY:  # pragma: no cover
        raise ParserError('lingpy must be installed to run this command!')

    def writer(*comps):
        return UnicodeWriter(args.repos.path('pkg', *comps), delimiter='\t')

    columns = ['LATEX', 'FEATURES', 'SOUND', 'IMAGE', 'COUNT', 'NOTE']
    bipa = args.repos.bipa
    for src, rows in args.repos.iter_sources(type='td'):
        args.log.info('TranscriptionData %s ...', src['NAME'])
        out = get_processed_transcription_data(src, rows, columns, bipa, args.log)
        with writer('transcriptiondata', f"{src['NAME']}.tsv") as w:
            w.writerows(out)

    count = 0
    with writer('soundclasses', 'lingpy.tsv') as w:
        w.writerow(['CLTS_NAME', 'BIPA_GRAPHEME'] + SOUNDCLASS_SYSTEMS)
        for grapheme, sound in sorted(bipa.sounds.items()):
            if not sound.alias:
                w.writerow(
                    [sound.name, grapheme]
                    + [token2class(grapheme, Model(cls)) for cls in SOUNDCLASS_SYSTEMS])
                count += 1
    args.log.info('SoundClasses: %s written to file.', count)
