from pyclts.models import *


def make_sound(cls):
    return cls(None, 'x')


def test_hash():
    snd = make_sound(Vowel)
    assert {snd: 1}[snd] == 1


def test_lru_cache():
    """Make sure the classmethod works, i.e. caches return values by class and not by instance."""
    info = Symbol.type.cache_info()
    assert info.misses <= info.maxsize

    for cls in [Symbol, Marker, Sound, Vowel]:
        for i in range(100):
            obj = make_sound(Marker)
            assert obj.type()

    newinfo = Symbol.type.cache_info()
    assert newinfo.hits >= info.hits + 100
    assert newinfo.misses <= newinfo.maxsize

    newinfo = Marker.type.cache_info()
    assert newinfo.hits >= info.hits + 100
    assert newinfo.misses <= newinfo.maxsize
