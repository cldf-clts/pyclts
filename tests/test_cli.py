import pathlib

from pyclts.__main__ import main


def test_features(capsys, repos):
    main(['--repos', str(repos), 'features'])
    out, err = capsys.readouterr()
    assert 'labialized' in out


def test_stats(capsys, tmp_repos):
    main(['--repos', str(tmp_repos), 'dump'])
    main(['--repos', str(tmp_repos), 'stats'])
    out, err = capsys.readouterr()
    assert 'STATS' in out


def test_tdstats(capsys, repos):
    main(['--repos', str(repos), 'tdstats'])


def test_sounds_(repos, capsys):
    main(['--repos', str(repos), 'sounds', 'a', 'kh', 'zz'])
    out, _ = capsys.readouterr()
    assert 'kʰ' in out


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


def test_dump(tmp_repos, tmpdir):
    p = pathlib.Path(str(tmpdir)) / 'test.zip'
    main(['--repos', str(tmp_repos), 'dump', '--destination', str(p)])
    assert tmp_repos.joinpath('data', 'graphemes.tsv').exists()
    assert p.exists()
