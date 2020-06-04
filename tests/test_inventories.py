import pytest
from pyclts.inventories import reduce_features, Inventory
from pathlib import Path
from pyclts.transcriptionsystem import TranscriptionSystem

def test_reduce_features():
    bipa = TranscriptionSystem(
            Path(__file__).parent.joinpath('repos', 'pkg',
                'transcriptionsystems', 'bipa'),
            Path(__file__).parent.joinpath('repos', 'pkg',
                'transcriptionsystems', 'transcription-system-metadata.json'),
            Path(__file__).parent.joinpath('repos', 'pkg',
                'transcriptionsystems', 'features.json'),
            )
    assert reduce_features('th', clts=bipa).s == 't'
    assert reduce_features('oe', clts=bipa).s == 'o'
    assert reduce_features('⁵⁵', clts=bipa).s == '⁵'


def test_Inventory():
    bipa = TranscriptionSystem(
            Path(__file__).parent.joinpath('repos', 'pkg',
                'transcriptionsystems', 'bipa'),
            Path(__file__).parent.joinpath('repos', 'pkg',
                'transcriptionsystems', 'transcription-system-metadata.json'),
            Path(__file__).parent.joinpath('repos', 'pkg',
                'transcriptionsystems', 'features.json'),
            )

    inv1 = Inventory.from_list('a', 'e', 'i', 'o', 'p', clts=bipa)
    inv2 = Inventory.from_list('a', 'e', 'i', 'œ', 'p', clts=bipa)
    inv3 = Inventory.from_list('a', 'e', 'i', 'æ', 'p', clts=bipa)
    assert inv1.similar(inv2, metric='strict') == inv1.similar(inv3, metric='strict')
    assert inv1.similar(inv2, metric='approximate') > inv1.similar(
            inv3, metric='approximate')
