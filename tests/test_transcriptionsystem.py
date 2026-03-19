import pytest

from pyclts.transcriptionsystem import TranscriptionSystem


def test_ts():
    with pytest.raises(ValueError):
        TranscriptionSystem(__file__, __file__)


def test_unknown_sound(bipa):
    assert bipa['AAː'].type == 'unknownsound'


def test_feature_system(asjp):
    assert 'affricate' in asjp.feature_system
    assert 'y' in asjp
