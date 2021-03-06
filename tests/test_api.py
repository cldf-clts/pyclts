import pytest

from pyclts.api import CLTS


@pytest.fixture
def sources(tmpdir):
    tmpdir.join('sources').mkdir()
    tmpdir.join('sources', 'index.tsv').write_text(
        'NAME\tDESCRIPTION\tREFS\tTYPE\tURITEMPLATE\ntest\t\t\ttd\t', 'utf8')
    tmpdir.join('sources', 'test').mkdir()
    tmpdir.join('sources', 'test', 'graphemes.tsv').write_text('GRAPHEME\tBIPA', 'utf8')


def test_iter_sources(sources, tmpdir):
    api = CLTS(repos=str(tmpdir))
    srcs = list(api.iter_sources(type='td'))
    assert len(srcs[0][1]) == 0
    assert srcs[0][0]['NAME'] == 'test'


def test_transcriptionsystem_custom(repos, api):
    assert api.transcriptionsystem(repos / 'pkg' / 'transcriptionsystems' / 'asjpcode')


def test_get_source(api):
    assert len(api.get_source('allenbai')) == 6


def test_diphthong(api):
    d = api.bipa['ai']
    assert 'diphthong' in d._features()
    assert 'from_centrality' in d.featuredict


def test_soundclass(api):
    sc = api.soundclass('sca')

    with pytest.raises(KeyError):
        sc.resolve_sound('xy')

    assert tuple(str(snd) for snd in sc("m")) == ("M",)
    assert tuple(str(snd) for snd in sc("m a")) == ("M", "A")
    assert tuple(str(snd) for snd in sc(["m", "a"])) == ("M", "A")

def test_transcriptiondata(api, repos):
    td = api.transcriptiondata('phoible')
    assert td.resolve_sound('a')
    with pytest.raises(KeyError):
        td.resolve_sound('xy')

    assert str(td.resolve_grapheme('kǂʼ')) == 'ǂ’'

    assert api.get_meta(td)
    assert api.transcriptiondata(repos / 'pkg' / 'transcriptiondata' / 'phoible.tsv')
