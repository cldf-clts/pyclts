import pytest

from pyclts.transcriptionsystem import TranscriptionSystem
from pyclts.systembase import TranscriptionBase


def test_TranscriptionBase(tmpdir):
    class TS(TranscriptionBase):
        def resolve_sound(self, sound):
            raise KeyError

    ts = TS(str(tmpdir))
    assert ts.get(None, 5) == 5


def test_ts():
    with pytest.raises(ValueError):
        TranscriptionSystem(__file__, __file__)


def test_unknown_sound(bipa):
    assert bipa['AAː'].type() == 'unknownsound'


def test_feature_system(asjp):
    assert 'affricate' in asjp.feature_system
    assert 'y' in asjp
