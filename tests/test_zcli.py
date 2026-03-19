import logging

from pyclts.__main__ import main as main_


def main(*args, **kw):
    kw['log'] = logging.getLogger(__name__)
    main_(*args, **kw)


def test_ls(capsys, repos):
    main(['--repos', str(repos), 'ls'])
    out, _ = capsys.readouterr()
    assert 'Setala' in out


def test_features(capsys, repos):
    main(['--repos', str(repos), 'features'])
    out, err = capsys.readouterr()
    assert 'labialized' in out


def test_stats(capsys, tmp_repos):
    main(['--repos', str(tmp_repos), 'dist'])
    main(['--repos', str(tmp_repos), 'stats'])
    out, err = capsys.readouterr()
    assert 'STATS' in out


def test_tdstats(capsys, repos):
    main(['--repos', str(repos), 'tdstats'])


def test_sounds_(repos, capsys):
    main(['--repos', str(repos), 'sounds', 'a', 'kh', 'zz'])
    out, _ = capsys.readouterr()
    assert 'kʰ' in out


def test_map(tmp_repos, capsys, fixtures):
    main(['--repos', str(tmp_repos), 'map', 'allenbai'])
    out, _ = capsys.readouterr()
    assert 'BIPA' in out


def test_make_dataset(tmp_repos, capsys, fixtures):
    main(['--repos', str(tmp_repos), 'make_dataset', 'allenbai'])
    out, _ = capsys.readouterr()


def test_test_dataset(tmp_repos, capsys, fixtures, caplog):
    main(['--repos', str(tmp_repos), 'test_dataset', 'allenbai'])
    out, _ = capsys.readouterr()
    graphemes = tmp_repos.joinpath('sources', 'allenbai', 'graphemes.tsv')
    orig = graphemes.read_text(encoding='utf8')
    graphemes.write_text(
        """BIPA	GRAPHEME	COUNT	SYMBOLS
<NA>	66	1	
a	a	9	◌a
u	a	9	◌a
A	x	9	◌a
ai	ai	1	◌a ◌i
ai	ai	1	◌a ◌i
ao	ao	3	◌a ◌o
ã	ã	5	◌a ◌̃
ão	ão	2	◌a ◌̃ ◌o
	ãx	2	◌a ◌̃ ◌o
""", encoding='utf8')
    main(['--repos', str(tmp_repos), 'test_dataset', 'allenbai'])
    out, _ = capsys.readouterr()
    assert caplog.records[-1].levelname == 'WARNING'
    graphemes.write_text(orig, encoding='utf8')


def test_table(capsys, repos):
    main(['--repos', str(repos), 'table', 'a', 'kh', 'zz'])
    out, err = capsys.readouterr()
    assert '# vowel' in out
    assert '# consonant' in out
    assert '# Unknown sounds' in out
    main(['--repos', str(repos), 'table', 'a', 'kh', 'zz', '--filter', 'unknown'])
    main(['--repos', str(repos), 'table', 'a', 'kh', 'zz', '--filter', 'known'])
    main(['--repos', str(repos), 'table', 'a', 'kh', 'zz', '--filter', 'generated'])


def test_make_pkg_and_app(capsys, tmp_repos, mocker):
    mocker.patch('pyclts.commands.make_pkg.LINGPY', True)
    mocker.patch('pyclts.commands.make_pkg.token2class', mocker.Mock(return_value='a'))
    mocker.patch('pyclts.commands.make_pkg.Model', mocker.Mock())
    main(['--repos', str(tmp_repos), 'make_pkg'])
    tmp_repos.joinpath('app').mkdir()
    main(['--repos', str(tmp_repos), 'make_app'])
    assert tmp_repos.joinpath('app', 'data.js').exists()
    main(['--repos', str(tmp_repos), 'test', '--test'])


def test_dist(tmp_repos, tmp_path):
    p = tmp_path / 'test.zip'
    main(['--repos', str(tmp_repos), 'dist', '--destination', str(p)])
    assert tmp_repos.joinpath('data', 'graphemes.tsv').exists()
    assert p.exists()
