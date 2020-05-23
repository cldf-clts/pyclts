from pyclts.ipachart import *


def test_ipa_charts():
    inventory = [
        Segment('x', 'voiced alveolar nasal consonant', href='http://example.org'),
        Segment('a', 'rounded close back vowel', href='http://example.org')
    ]
    html, covered = ipa_charts(inventory)
    assert covered == {0, 1}
