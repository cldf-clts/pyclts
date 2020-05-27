from pyclts.ipachart import *


def test_ipa_charts():
    inventory = [
        Segment('x', 'voiced alveolar nasal consonant', href='http://example.org', css_class='abc'),
        Segment('a', 'rounded close back vowel', href='http://example.org', css_class='abc')
    ]
    html, covered = ipa_charts(inventory)
    assert covered == {0, 1}
    html, covered = ipa_charts(inventory, colorspec={'abc': ('red', 'solid 1px green')})
    assert 'abc' in html and 'green' in html
