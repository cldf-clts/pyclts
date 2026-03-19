import random

from pyclts.features import *


def make_one(cls, rand=False):
    def get_value(v):
        if rand:
            return random.choice(v)
        return v[0]
    return cls(**{k: get_value(v) for k, v in cls.valid_values().items()})


def test_excluded():
    assert 'laminal' in ConsonantFeatures.feature_values_excluded_in_str()


def test_lru_cache():
    """Make sure the classmethod works, i.e. caches return values by class and not by instance."""
    info = ConsonantFeatures.valid_values.cache_info()
    assert info.misses <= info.maxsize

    for i in range(100):
        cf = make_one(ConsonantFeatures, rand=True)
        assert cf.valid_values()

    newinfo = ConsonantFeatures.valid_values.cache_info()
    assert newinfo.hits >= info.hits + 100
    assert newinfo.misses <= newinfo.maxsize
