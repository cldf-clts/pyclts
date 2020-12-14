"""
Prepare transcriptiondata from the transcription sources.
"""
from uritemplate import URITemplate
from clldutils.clilib import ParserError
from csvw.dsv import UnicodeWriter
from pyclts.commands.make_dataset import process_transcription_data

try:
    from lingpy.sequence.sound_classes import token2class
    from lingpy.data import Model
    LINGPY = True
except ImportError:
    LINGPY = False
    token2class = None
    Model = None

from pyclts.soundclasses import SOUNDCLASS_SYSTEMS


def run(args):
    if not LINGPY:
        raise ParserError('lingpy must be installed to run this command!')

    def writer(*comps):
        return UnicodeWriter(args.repos.path('pkg', *comps), delimiter='\t')

    columns = ['LATEX', 'FEATURES', 'SOUND', 'IMAGE', 'COUNT', 'NOTE']
    bipa = args.repos.bipa
    for src, rows in args.repos.iter_sources(type='td'):
        args.log.info('TranscriptionData {0} ...'.format(src['NAME']))
        uritemplate = URITemplate(src['URITEMPLATE']) if src['URITEMPLATE'] else None
        out = process_transcription_data(
            rows, columns, src, uritemplate, bipa, args)

        found = len([o for o in out if o[0] != '<NA>'])
        args.log.info('... {0} of {1} graphemes found ({2:.0f}%)'.format(
            found, len(out), found / len(out) * 100))
        with writer('transcriptiondata', '{0}.tsv'.format(src['NAME'])) as w:
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
    args.log.info('SoundClasses: {0} written to file.'.format(count))
