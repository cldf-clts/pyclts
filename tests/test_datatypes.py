import pytest

from pyclts.datatypes import TranscriptionSystem
from pyclts.datatypes_util import TranscriptionBase


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


@pytest.mark.parametrize('grapheme', ['dʱʷ', 'e̤ː', 'ai', 'kg'])
def test_generated_sound_lookup(bipa, grapheme):
    sound = bipa[grapheme]
    assert sound.generated
    assert sound.featureset not in bipa.features_to_sound
    resolved = bipa[sound]
    assert resolved.name == sound.name
    assert str(resolved) == str(sound)


@pytest.mark.parametrize('grapheme', ['dʱʷ', 'e̤ː', 'kʷʰ', 'ǀ'])
def test_sound_lookup_other_system(bipa, asjp, grapheme):
    sound = bipa[grapheme]
    if sound.featureset in asjp.features_to_sound:
        assert asjp[sound] is asjp.features_to_sound[sound.featureset]
        return
    with pytest.raises(KeyError):
        asjp[sound]
    sentinel = object()
    assert asjp.get(sound, default=sentinel) is sentinel
