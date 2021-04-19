import pytest
from pyclts.inventories import reduce_features, Inventory, Phoneme
from pyclts.transcriptionsystem import TranscriptionSystem


@pytest.fixture
def bipa(repos):
    return TranscriptionSystem(
        repos / "pkg" / "transcriptionsystems" / "bipa",
        repos / "pkg" / "transcriptionsystems" / "transcription-system-metadata.json",
        repos / "pkg" / "transcriptionsystems" / "features.json",
    )


def test_reduce_features(bipa):
    assert reduce_features("th", ts=bipa).s == "t"
    assert reduce_features("oe", ts=bipa).s == "o"
    assert reduce_features("⁵⁵", ts=bipa).s == "⁵"


def test_Phoneme(bipa):
    soundA = bipa['K']
    soundB = bipa['U']
    soundC = bipa['K']

    phonA = Phoneme(grapheme=str(soundA), sound=soundA)
    phonB = Phoneme(grapheme=str(soundB), sound=soundB)
    phonC = Phoneme(grapheme=str(soundC), sound=soundC)

    assert phonA.type == 'unknownsound'

    assert phonA.similarity(phonB) == 0
    assert phonA.similarity(phonC) == 1



def test_Inventory(bipa):
    inv1 = Inventory.from_list("a", "e", "i", "o", "p", ts=bipa)
    inv2 = Inventory.from_list(
            "a", "e", "i", "œ", "p", ts=bipa, id='ID', language='language')
    inv3 = Inventory.from_list("a", "e", "i", "æ", "p", ts=bipa)
    inv4 = Inventory.from_list("u", "K", "+", "a", ts=bipa)
    inv5 = Inventory.from_list("a", "e", "i", ts=bipa)
    inv6 = Inventory.from_list("p", "t", "k", ts=bipa)
    assert inv1.language is None
    assert inv1.id is None
    assert inv2.language == 'language'
    assert inv2.id == 'ID'
    inv1.tabulate()
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

    # check for inventories without similarities
    assert inv5.approximate_similarity(inv6, aspects=['consonants', 'vowels']) == 0
    assert len(inv5) == 3

    # test for new properties
    inv1 = Inventory.from_list('uː', 'u', 'ui', ts=bipa)
    assert len(inv1.vowel_sounds) == 3
    assert len(inv1.vowels) == 2
    assert len(inv1.vowels_by_quality) == 1

    inv2 = Inventory.from_list('tː', 't', 'k', ts=bipa)
    assert len(inv2.consonant_sounds) == 3
    assert len(inv2.consonants_by_quality) == 2
    
    inv3 = Inventory.from_list('p', '²', ts=bipa)
    assert len(inv3.segments) == 1

    inv4 = Inventory.from_list('tː', 'k', ts=bipa)
    inv5 = Inventory.from_list('oː', 'a', ts=bipa)
    assert len(inv4.consonants_by_quality) == 2
    assert len(inv5.vowels_by_quality) == 2
