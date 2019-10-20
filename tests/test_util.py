from pyclts.util import *


def test_TranscriptionBase(tmpdir):
    class TS(TranscriptionBase):
        def resolve_sound(self, sound):
            raise KeyError

    ts = TS(str(tmpdir))
    assert ts.get(None, 5) == 5
