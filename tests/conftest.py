from pathlib import Path
import shutil

import pytest

from pyclts import CLTS


@pytest.fixture
def tests_dir():
    return Path(__file__).parent


@pytest.fixture(scope='session')
def repos():
    return Path(__file__).parent / 'repos'


@pytest.fixture
def fixtures(tmpdir, tests_dir):
    shutil.copytree(str(tests_dir / 'fixtures'), str(tmpdir.join('fixtures')))
    return Path(str(tmpdir)) / 'fixtures'


@pytest.fixture
def tmp_repos(tmpdir, tests_dir):
    shutil.copytree(str(tests_dir / 'repos'), str(tmpdir.join('repos')))
    return Path(str(tmpdir)) / 'repos'


@pytest.fixture(scope='session')
def api(repos):
    return CLTS(repos)


@pytest.fixture(scope='session')
def bipa(api):
    return api.bipa


@pytest.fixture(scope='session')
def asjp(api):
    return api.transcriptionsystem('asjpcode')
