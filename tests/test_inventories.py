import pytest
from pyclts.inventories import reduce_features, Inventory, Phoneme
from pathlib import Path
from pyclts.transcriptionsystem import TranscriptionSystem


def test_reduce_features():
    bipa = TranscriptionSystem(
        Path(__file__).parent.joinpath("repos", "pkg", "transcriptionsystems", "bipa"),
        Path(__file__).parent.joinpath(
            "repos", "pkg", "transcriptionsystems", "transcription-system-metadata.json"
        ),
        Path(__file__).parent.joinpath(
            "repos", "pkg", "transcriptionsystems", "features.json"
        ),
    )
    assert reduce_features("th", ts=bipa).s == "t"
    assert reduce_features("oe", ts=bipa).s == "o"
    assert reduce_features("⁵⁵", ts=bipa).s == "⁵"


def test_Phoneme():
    bipa = TranscriptionSystem(
        Path(__file__).parent.joinpath("repos", "pkg", "transcriptionsystems", "bipa"),
        Path(__file__).parent.joinpath(
            "repos", "pkg", "transcriptionsystems", "transcription-system-metadata.json"
        ),
        Path(__file__).parent.joinpath(
            "repos", "pkg", "transcriptionsystems", "features.json"
        ),
    )
    soundA = bipa['K']
    soundB = bipa['U']
    soundC = bipa['K']

    phonA = Phoneme(grapheme=str(soundA), sound=soundA, type='unknownsound')
    phonB = Phoneme(grapheme=str(soundB), sound=soundB, type='unknownsound')
    phonC = Phoneme(grapheme=str(soundC), sound=soundC, type='unknownsound')

    assert phonA.similarity(phonB) == 0
    assert phonA.similarity(phonC) == 1



def test_Inventory():
    bipa = TranscriptionSystem(
        Path(__file__).parent.joinpath("repos", "pkg", "transcriptionsystems", "bipa"),
        Path(__file__).parent.joinpath(
            "repos", "pkg", "transcriptionsystems", "transcription-system-metadata.json"
        ),
        Path(__file__).parent.joinpath(
            "repos", "pkg", "transcriptionsystems", "features.json"
        ),
    )

    inv1 = Inventory.from_list("a", "e", "i", "o", "p", ts=bipa)
    inv2 = Inventory.from_list("a", "e", "i", "œ", "p", ts=bipa)
    inv3 = Inventory.from_list("a", "e", "i", "æ", "p", ts=bipa)
    inv4 = Inventory.from_list("u", "K", "+", "a", ts=bipa)
    assert 'K' in inv4.unknownsounds
    assert '+' in inv4.markers
    assert inv1.strict_similarity(inv2) == inv1.strict_similarity(inv3)
    assert inv1.approximate_similarity(inv2) > inv1.approximate_similarity(
        inv3)

    assert inv1.strict_similarity(inv2) == pytest.approx(0.666666, 0.0001)
    assert inv1.strict_similarity(
        inv2, aspects=["consonants", "vowels"]) == pytest.approx(0.8, 0.0001)
    assert inv1.approximate_similarity(inv2) == pytest.approx(0.866666, 0.0001)
    assert inv1.approximate_similarity(
        inv2, aspects=["consonants", "vowels"]) == pytest.approx(0.916666, 0.0001)
