import pytest
from pyclts.inventories import reduce_features, Inventory

def test_reduce_features():
    assert reduce_features('th').s == 't'
    assert reduce_features('oe').s == 'o'
    assert reduce_features('⁵⁵').s == '⁵'


def test_Inventory():
    inv1 = Inventory.from_list('a', 'e', 'i', 'o', 'p')
    inv2 = Inventory.from_list('a', 'e', 'i', 'œ', 'p')
    inv3 = Inventory.from_list('a', 'e', 'i', 'æ', 'p')
    assert inv1.similar(inv2, metric='strict') == inv1.similar(inv3, metric='strict')
    assert inv1.similar(inv2, metric='approximate') > inv1.similar(
            inv3, metric='approximate')
