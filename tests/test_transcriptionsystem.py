import pytest

from pyclts.transcriptionsystem import TranscriptionSystem


def test_ts():
    with pytest.raises(ValueError):
        TranscriptionSystem(__file__, __file__, __file__)
