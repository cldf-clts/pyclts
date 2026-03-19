from pyclts.models import *


def make_sound(cls):
    return cls(None, 'x')


def test_hash():
    snd = make_sound(Vowel)
    assert {snd: 1}[snd] == 1
