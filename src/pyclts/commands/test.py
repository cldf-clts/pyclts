"""
Check repository data for consistency
"""
import argparse
import pathlib

from csvw.dsv import reader

import pyclts


def register(parser):
    parser.add_argument(
        '--test',
        action='store_true',
        default=False,
        help=argparse.SUPPRESS,
    )


def run(args):
    clts = args.repos

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
    # bipa should always be able to be translated to
    for sound in asjp:
        if sound not in bipa:
            assert '<?>' not in str(bipa[asjp[sound].name])
    for sound in gld:
        if sound not in bipa:
            assert '<?>' not in str(bipa[gld[sound].name])
    for sound in bipa:
        if bipa[sound].type != 'unknownsound' and not bipa[sound].alias:
            if sound != str(bipa[sound]):
                raise ValueError
        elif bipa[sound].type == 'unknownsound':
            raise ValueError
    for sound in gld:
        if gld[sound].type != 'unknownsound' and not gld[sound].alias:
            if sound != str(gld[sound]):
                raise ValueError
        elif gld[sound].type == 'unknownsound':
            raise ValueError
    for sound in asjp:
        if asjp[sound].type != 'unknownsound' and not asjp[sound].alias:
            if sound != str(asjp[sound]):
                raise ValueError
        elif asjp[sound].type == 'unknownsound':
            raise ValueError

    # important test for alias
    assert str(bipa['d̤ʷ']) == str(bipa['dʷʱ']) == str(bipa['dʱʷ'])


def read_tests(name):
    return reader(pathlib.Path(pyclts.__file__).parent / 'data' / name, delimiter='\t', dicts=True)


def test_sounds(bipa, log):
    for test in read_tests('test_data.tsv'):
        del test['bipa']
        if None in test:
            del test[None]
        try:
            _test_sounds(bipa, **{k.replace('-', '_'): v for k, v in test.items()})
        except AssertionError as e:
            log.warning('{0}\t{1}'.format(test['source'], e))


def test_clicks(bipa):
    for test in read_tests('clicks.tsv'):
        _test_clicks(bipa, test['GRAPHEME'], test['MANNER'])


def _test_clicks(bipa, grapheme, gtype):
    if gtype == 'stop-cluster':
        assert bipa[grapheme].type == 'cluster'


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
        assert sound.name == kw.name
        assert sound.codepoints == kw.codepoints, "Not matching codepoints"
