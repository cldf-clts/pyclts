"""
Check repository data for consistency

FIXME: must also check implementation in pyclts/features.py for compatibility with
pkg/transcriptionsystems/features.json
"""
import pathlib
import argparse

import pyclts
from pyclts.util import dict_reader


def register(parser):  # pylint: disable=C0116
    parser.add_argument(
        '--test',
        action='store_true',
        default=False,
        help=argparse.SUPPRESS,
    )


def run(args):  # pylint: disable=C0116
    clts = args.repos

    for src in clts.meta:
        for ref in src['REFS']:
            assert ref in clts.references, f'Missing bibtex key: {ref}'

    if not args.test:  # pragma: no cover
        test_transcriptiondata(
            clts.soundclass('sca'),
            clts.soundclass('dolgo'),
            clts.soundclass('asjp'),
            clts.transcriptiondata('phoible'),
            clts.transcriptionsystem('bipa'))
        test_transcription_system_consistency(
            *[clts.transcriptionsystem(key) for key in ['bipa', 'asjpcode', 'gld']])
    test_sounds(clts.bipa, args.log)
    test_clicks(clts.bipa)


def test_transcriptiondata(sca, dolgo, asjpd, phoible, bipa):  # pragma: no cover
    """Test samples of transcription data"""
    seq = 'tʰ ɔ x ˈth ə r A ˈI ʲ'
    seq2 = 'th o ?/x a'
    seq3 = 'th o ?/ a'
    seq4 = 'ǃŋ i b ǃ'

    assert dolgo(seq) == list('TVKTVR000')
    assert sca(seq2)[2] == 'G'
    assert asjpd(seq2)[2] == 'x'
    assert sca(seq3)[2] == '0'

    # these tests need to be adjusted once lingpy accepts click sounds
    assert sca(seq4)[0] == '0'
    assert asjpd(seq4)[0] == '0'
    assert sca(seq4)[3] == '!'
    assert asjpd(seq4)[3] == '!'

    # test data from sound name
    assert sca.resolve_sound(bipa['ʰb']) == 'P'
    assert sca.resolve_sound(bipa['ae']) == 'A'
    assert sca.resolve_sound(bipa['tk']) == 'T'
    assert phoible.resolve_sound('m') == 'm'
    try:
        phoible.resolve_sound(bipa['tk'])
        raise ValueError()
    except KeyError:
        pass


def test_transcription_system_consistency(bipa, asjp, gld):  # pragma: no cover
    """Test all sounds in transcription systems."""
    # bipa should always be able to be translated to
    for system in (asjp, gld):
        for sound in system:
            if sound not in bipa:
                assert '<?>' not in str(bipa[system[sound].name])

    for system in (bipa, gld, asjp):
        for sound in system:
            if system[sound].type != 'unknownsound' and not system[sound].alias:
                if sound != str(system[sound]):
                    raise ValueError
            elif system[sound].type == 'unknownsound':
                raise ValueError

    # important test for alias
    assert str(bipa['d̤ʷ']) == str(bipa['dʷʱ']) == str(bipa['dʱʷ'])


def read_tests(name):  # pylint: disable=C0116
    return dict_reader(pathlib.Path(pyclts.__file__).parent / 'data' / name)


def test_sounds(bipa, log):  # pylint: disable=C0116
    for test in read_tests('test_data.tsv'):
        del test['bipa']
        if None in test:
            del test[None]
        try:
            _test_sounds(bipa, **{k.replace('-', '_'): v for k, v in test.items()})
        except AssertionError as e:  # pragma: no cover
            log.warning('%s\t%s', test['source'], e)


def test_clicks(bipa):  # pylint: disable=C0116
    for test in read_tests('clicks.tsv'):
        _test_clicks(bipa, test['GRAPHEME'], test['MANNER'])


def _test_clicks(bipa, grapheme, gtype):
    if gtype == 'stop-cluster':
        assert bipa[grapheme].type == 'cluster', bipa[grapheme].type


def _test_sounds(bipa, **kw):
    """Test on a large pre-assembled dataset whether everything is consistent"""
    kw = argparse.Namespace(**kw)

    sound = bipa[kw.source]
    if sound.type not in ['unknownsound', 'marker']:
        if kw.nfd_normalized == '+':
            assert bipa[kw.source] != sound.source, "Sound does not resolve to itself"
        if kw.clts_normalized == "+":
            assert sound.normalized, "Sound not normalized"
        if kw.aliased == '+':
            assert sound.alias, "Sound not an alias"
        if kw.generated:
            assert sound.generated, "Sound not generated"
        if kw.stressed:
            assert sound.stress, "Sound not stressed"
        assert sound.name == kw.name, "Names not matched"
        assert sound.codepoints == kw.codepoints, "Not matching codepoints"
