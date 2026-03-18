import pytest

from pyclts.util import *

def test_jaccard():

    assert jaccard(set(), set()) == 0

def test_TranscriptionBase(tmpdir):
    class TS(TranscriptionBase):
        def resolve_sound(self, sound):
            raise KeyError

    ts = TS(str(tmpdir))
    assert ts.get(None, 5) == 5


@pytest.mark.parametrize(
    'kw,expected_substring',
    [
        (dict(in_header='Sub', level=3, new='\nnew'), 'Subheader\n\nnew'),
        (dict(in_header='New', level=3, new='new'), '### New\n\nnew'),
    ]
)
def test_upsert_section(tmp_path, kw, expected_substring):
    md = """
# Title

## Header1

text1

### Subheader

text1.1

#### Subsub

text1.1.1

## Header2

text2
"""
    p = tmp_path / 'text.md'
    p.write_text(md)
    upsert_section(p, **kw)
    assert expected_substring in p.read_text()
