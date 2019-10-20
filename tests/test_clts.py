import pytest

from pyclts.models import Marker, UnknownSound, is_valid_sound, Symbol, Sound


def test_TranscriptionBase_translate(bipa, asjp):
    assert bipa.translate('ts a', asjp) == 'c E'
    assert asjp.translate('c a', bipa) == 'ts ɐ'


def test_is_valid_sound(bipa):
    assert not is_valid_sound(bipa['_'], bipa)
    assert is_valid_sound(bipa['ä'], bipa)


def test_getitem(bipa):
    s = bipa['a']
    assert bipa[s] == s
    assert bipa[s.name] == s


def test_ts_contains(bipa, asjp):
    assert bipa['ts'] in asjp


def test_ts_equality(bipa, asjp):
    asjp_ts = asjp[bipa['ts']]
    assert bipa['ts'] == asjp_ts


def test_examples(bipa):
    sound = bipa['dʷʱ']
    assert sound.name == 'labialized breathy voiced alveolar stop consonant'
    assert sound.generated
    assert not sound.alias
    assert sound.codepoints == 'U+0064 U+02b7 U+02b1'
    assert sound.uname == 'LATIN SMALL LETTER D / MODIFIER LETTER SMALL W / MODIFIER LETTER SMALL H WITH HOOK'
    sound = bipa['dʱʷ']
    assert sound.name == 'labialized breathy voiced alveolar stop consonant'
    assert sound.generated
    assert sound.alias
    assert sound.codepoints == 'U+0064 U+02b7 U+02b1'


def test_different_conversions(bipa):
    string = 't e _ s 0 t + i n g'
    as_symbols = bipa(string, default=None)
    by_parts = [bipa[s] for s in string.split()]
    assert as_symbols == by_parts


#def test_asjp_from_symbols(bipa, asjpd):
#    string = 't e _ s t + i n g'
#    as_symbols = bipa(string, default=None)
#    for st, sy in zip(string.split(), as_symbols):
#        assert asjpd[st] == asjpd[sy]


def test_double_wrap(bipa):
    string = 't e _ s 0 t + i n g'
    as_symbols = bipa(string, default=None)
    assert ' '.join(str(s) for s in as_symbols) == string
    double_wrap = [bipa[s] for s in as_symbols]
    assert ' '.join(str(s) for s in double_wrap) == string


def test_parse(bipa):
    assert all(bipa[s].generated for s in ['ʰdʱ', "ˈa", 'á'])
    assert all(str(bipa[s]) == s for s in ['a', 't'])

    a = bipa['a']
    comps = a.name.split()
    assert bipa[' '.join(list(reversed(comps[:-2])) + [comps[-1]])]

    # diphthongs
    for s in ['ao', 'ea', 'ai', 'ua']:
        res = bipa[s]
        assert res.type == 'diphthong'
        assert res.name.endswith('diphthong')
        assert s == str(s)

    # clusters
    for s in ['tk', 'pk', 'dg', 'bdʰ']:
        res = bipa[s]
        assert res.type == 'cluster'
        assert 'cluster' in res.name
        assert s == str(s)

    # go for bad diacritics in front and end of a string
    assert bipa['*a'].type == 'unknownsound'
    assert bipa['a*'].type == 'unknownsound'

    # marker
    assert isinstance(bipa['_'], Marker)

    # decorated marker
    assert isinstance(bipa['_\u0329'], UnknownSound)


def test_call(bipa):
    assert bipa('th o x t a')[0].alias


def test_get(bipa):
    "test for the case that we have a new default"
    assert bipa.get('A', '?') == '?'


@pytest.mark.parametrize(
    "name,check",
    [
        (
            'from unrounded open front to unrounded close-mid front diphthong',
            lambda s: s.grapheme == 'ae'),
        (
            'from voiceless alveolar stop to voiceless velar stop cluster',
            lambda s: s.grapheme == 'tk'),
        ('pre-aspirated voiced bilabial nasal consonant', lambda s: s.generated),
        ('voiced nasal bilabial consonant', lambda s: not s.generated),
        # complex sounds are always generated
        ('ae', lambda s: s.generated),
        ('tk', lambda s: s.generated),
    ]
)
def test_sound_from_name(name, check, bipa):
    assert check(bipa[name])


def test_sound_from_name_error(bipa):
    with pytest.raises(ValueError):
        _ = bipa['very bad feature voiced labial stop consonant']

    with pytest.raises(ValueError):
        _ = bipa._from_name('very bad feature with bad consonantixs')

    with pytest.raises(ValueError):
        _ = bipa._from_name('from something to something diphthong')

    with pytest.raises(ValueError):
        _ = bipa._from_name('something diphthong')


def test_models(bipa, asjp):
    sym = Symbol(ts=bipa, grapheme='s', source='s', generated=False, note='')
    assert str(sym) == sym.source == sym.grapheme
    assert sym == sym
    assert not sym.name
    assert sym.uname == "LATIN SMALL LETTER S"

    # equality tests in model for sound
    s1 = bipa['t']
    s2 = 't'
    assert s1 != s2
    assert not Sound(ts=None, grapheme='a') == 5

    # repr test for sound
    assert s1.name in repr(s1)

    # test the table function
    assert s1.table[1] == 'voiceless'
    assert '|' in bipa["ts'"].table[0]

    # test table for generated entities
    assert bipa['tk'].table[1] == bipa['t'].name

    # test the unicode name
    assert Symbol(ts='', grapheme=[['1', '2'], '2'], source='').uname == '-'
    s = Symbol(ts=None, grapheme='\x84')  # U+0084 <control>
    assert s.uname == '?'

    # test complex sound
    assert str(bipa['ae']) == 'ae'

    # test equality of symbols
    assert Symbol(ts=bipa, grapheme='1', source='1') != Symbol(
        ts=asjp, grapheme='1', source='1')

    assert pytest.approx(1.0) == bipa['t'].similarity(asjp['t'])
