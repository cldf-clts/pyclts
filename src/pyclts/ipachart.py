"""
IPA charts are the most common device to visualize sound inventories.

See also https://en.wikipedia.org/wiki/International_Phonetic_Alphabet_chart
"""
import io
import copy
import pathlib
from typing import TYPE_CHECKING, Literal, Union, Optional
import functools
from collections.abc import Iterable, Generator
import dataclasses
from xml.etree import ElementTree as et

if TYPE_CHECKING:
    from pyclts.models import Sound


__all__ = ['Segment', 'VowelTrapezoid', 'PulmonicConsonants', 'ipa_charts']
# Map class names to pairs (fill, outline):
ColorSpecType = dict[Union[str, None], tuple[str, str]]


@dataclasses.dataclass
class Segment:
    """
    Bag of attributes controlling display of a segment in an IPA chart.
    """
    sound_bipa: str
    sound_name: str
    label: str = None
    href: str = None
    css_class: str = None
    title: str = None

    def __post_init__(self):
        assert isinstance(self.sound_bipa, str)
        assert isinstance(self.sound_name, str)
        if not self.label:
            self.label = self.sound_bipa
        if not self.title:
            self.title = self.sound_name

    @classmethod
    def from_sound(cls, sound: 'Sound', **kw) -> 'Segment':
        """Create a segment from a sound."""
        return cls(sound_bipa=str(sound), sound_name=sound.name, **kw)  # pragma: no cover

    @functools.cached_property
    def features(self) -> set[str]:
        """Set of features of the associated sound."""
        return set(s.replace('-', '') for s in self.sound_name.split())

    @property
    def link_attrib(self) -> dict[Literal['href', 'class'], str]:
        """Extract link attributes from the segment data."""
        res = {}
        if self.href:
            res['href'] = self.href
        if self.css_class:
            res['class'] = self.css_class
        return res

    @property
    def html_link_attrib(self) -> dict[Literal['href', 'class', 'title'], str]:
        """HTML links also should have a title."""
        res = self.link_attrib
        res.update(title=self.title)
        return res


def svg_css(colorspec: Optional[ColorSpecType] = None) -> Generator[str, None, None]:
    """
    :param colorspec:
    :return:
    """
    colorspec = colorspec or {None: ('black', 'solid 1px white')}
    yield "@namespace svg url(http://www.w3.org/2000/svg);"
    yield "svg|a:link, svg|a:visited {cursor: pointer;}"
    yield f"svg|a text, text svg|a {{fill: {colorspec.get(None, ('black', None))[0]};}}"
    yield f"svg|a {{outline: solid 1px {colorspec.get(None, (None, 'white'))[1]};}}"
    yield "svg|a:hover, svg|a:active {outline: dotted 1px blue;}"

    for cls, (fill, outline) in colorspec.items():
        if cls:
            if fill:
                yield f"svg|a.{cls} text, text svg|a.{cls} {{fill: {fill};}}"
            if outline:
                yield f"svg|a.{cls} {{outline: {outline};}}"
                # Unfortunately, there is no outline property in the SVG spec, see
                # https://stackoverflow.com/q/13387851
                # So as a fallback, we add a text-decoration:
                yield f"svg|a.{cls} {{text-decoration: underline;}}"
                yield f"svg|a.{cls} {{text-decoration-style: {outline.split()[0]};}}"
                yield f"svg|a.{cls} {{text-decoration-color: {outline.split()[-1]};}}"


class Diagram:
    """
    A visualization of a group of sounds, e.g. vowels in the "trapezoid" or consonants in a table.

    Usage:
    >>> d = Diagram()
    >>> covered = d.fill_slots(inventory)
    >>> html, css = d.render(colorspec)
    """
    __id__ = None  # HTML element id
    __fname__ = None  # Template filename
    __extend_features__ = None

    def __init__(self, id_=None):
        """
        :param id_: Pass a custom element ID to overwrite the default (e.g. to place multiple \
        diagrams of the same type on one page)
        """
        self._id = id_
        self.tree = et.parse(str(pathlib.Path(__file__).parent / self.__fname__))
        self.slots: dict[frozenset[str], tuple[et.Element, list[Segment]]] = {}
        self.exclusive = set()

    @property
    def id(self):  # pylint: disable=C0116
        return self._id or self.__id__

    def iter_slots(self) -> Generator[tuple[Iterable[str], et.Element]]:
        """
        Diagrams must provide a generator of the slots they provide as pairs (features, element),
        where `features` is a set of CLTS features (with NON<feature> specifying absence of a
        feature) and `element` is the ElementTree element where matching segments should be
        appended.
        """
        raise NotImplementedError()  # pragma: no cover

    def fill_slots(self, inventory: Iterable[Segment]) -> set[int]:
        """
        Assign matching segments to diagram slots.

        :param inventory: `list` of `Segment` instances.
        :return: `set` of inventory indices which have been assigned to slots.
        """
        self.slots: dict[frozenset[str], tuple[et.Element, list[Segment]]] = {}
        for features, element in self.iter_slots():
            features = set(features)
            if self.__extend_features__:
                features = features.union(self.__extend_features__)
            self.slots[frozenset(features)] = (element, [])
        covered = set()
        for i, segment in enumerate(inventory):
            features = copy.copy(segment.features)
            for ex in self.exclusive:
                if ex not in segment.features:
                    features.add('NON' + ex)
            for f, (_, segments) in self.slots.items():
                if f.issubset(features):
                    covered.add(i)
                    segments.append(segment)
                    break
        return covered

    def format_segment(
            self,
            element: et.Element,
            segment: Segment,
            is_last: bool,
            is_first: bool):
        """
        Diagrams must provide a method to format segments as ElementTree elements.
        """
        raise NotImplementedError()  # pragma: no cover

    def css(self, colorspec: ColorSpecType) -> Generator[str, None, None]:  # pylint: disable=C0116
        assert not colorspec or isinstance(colorspec, dict)  # pragma: no cover
        yield ''  # pragma: no cover

    def render(
            self,
            colorspec: Optional[ColorSpecType] = None
    ) -> tuple[str, Generator[str, None, None]]:
        """Render the diagram to HTML."""
        for e, segments in self.slots.values():
            for i, segment in enumerate(segments, start=1):
                self.format_segment(e, segment, i == len(segments), i == 0)

        self.tree.getroot().attrib['id'] = self.id
        o = io.BytesIO()
        self.tree.write(o)
        return o.getvalue().decode('utf8'), self.css(colorspec)


class PulmonicConsonants(Diagram):
    """The consonants table."""
    __id__ = 'pulmonic-consonants'
    __fname__ = 'consonants.html'
    __extend_features__ = frozenset({'consonant'})

    def iter_slots(self):  # pylint: disable=C0116
        for e in self.tree.findall('.//td'):
            if 'class' in e.attrib:
                for attrs in e.attrib['class'].split():
                    attrs = attrs.split('-')
                    for att in attrs:
                        if att.startswith('NON'):
                            self.exclusive.add(att[3:])
                    yield attrs, e

    def format_segment(self, element, segment, is_last, is_first):  # pylint: disable=C0116
        ee = et.SubElement(element, 'a', attrib=segment.html_link_attrib)
        ee.text = segment.label
        if not is_last:
            ee.tail = '\xa0'  # pragma: no cover

    def css(self, colorspec: ColorSpecType) -> Generator[str, None, None]:  # pylint: disable=C0116
        colorspec = colorspec or {None: ('black', 'solid 1px white')}
        yield f"#{self.id} a {{text-decoration: none; font-size: smaller;}}"
        yield f"#{self.id} a {{color: {colorspec.get(None, ('black', None))[0]};}}"
        yield (f"#{self.id} a "
               f"{{outline: solid 1px {colorspec.get(None, (None, 'solid 1px white'))[1]};}}")
        for cls, (fill, outline) in colorspec.items():
            if cls:
                if fill:
                    yield f"#{self.id} a.{cls} text, text svg|a.{cls} {{fill: {fill};}}"
                    yield f"#{self.id} a.{cls} {{color: {fill};}}"
                if outline:
                    yield f"#{self.id} a.{cls} {{outline: {outline};}}"


class VowelTrapezoid(Diagram):
    """The IPA vowel trapezoid."""
    __id__ = 'vowel-trapezoid'
    __fname__ = 'vowels.svg'
    __extend_features__ = frozenset({'vowel'})

    def iter_slots(self):  # pylint: disable=C0116
        ns = {'svg': "http://www.w3.org/2000/svg"}
        et.register_namespace('', ns['svg'])
        for e in self.tree.findall('.//svg:text', ns):
            if 'id' in e.attrib:
                yield e.attrib['id'].split('-'), e

    def format_segment(self, element, segment, is_last, is_first):  # pylint: disable=C0116
        ee = et.SubElement(element, '{http://www.w3.org/2000/svg}a', attrib=segment.link_attrib)
        title = et.SubElement(ee, '{http://www.w3.org/2000/svg}title')
        title.text = segment.title
        ee.text = segment.label
        if not is_last:
            ee.tail = ' '  # pragma: no cover

    def css(self, colorspec: ColorSpecType) -> Generator[str, None, None]:  # pylint: disable=C0116
        yield f"#{self.id} {{height: 300px; width: 100%; min-width: 800px;}}"
        yield f"#{self.id} .label {{font-size: 150%;}}"
        yield f"#{self.id} .glyph {{font-size: 170%;}}"

    def render(  # pylint: disable=C0116
            self,
            colorspec: Optional[ColorSpecType] = None,
    ) -> tuple[str, Generator[str, None, None]]:
        r = self.tree.getroot()
        del r.attrib['width']
        del r.attrib['height']
        style = et.SubElement(r, '{http://www.w3.org/2000/svg}style')
        style.text = "\n".join(svg_css(colorspec)) + "\n"
        res, css = Diagram.render(self)
        res = res.replace('#666666', '#dddddd')
        return f'<figure>{res}<figcaption>Vowels</figcaption></figure>', css


def ipa_charts(inventory: Iterable[Segment], colorspec: Optional[ColorSpecType] = None):
    """
    Slots matching segments into a set of predefined diagrams.

    :param inventory:
    :param colorspec:
    :return: A pair (html, covered)
    """
    css, html, covered = [], [], set()

    for diagram in [
        PulmonicConsonants(),
        VowelTrapezoid(),
    ]:
        covered = covered.union(diagram.fill_slots(inventory))
        html_, css_ = diagram.render(colorspec)
        html.append(html_)
        css.extend(list(css_))

    return """\
<html>
<head>
<style>
body {{font-family: sans-serif}}
table caption {{text-align: left;}}
figure {{display: table; margin-left: 0px;}}
figcaption {{display: table-caption; caption-side: top; font-size: 120%;}}
{}
</style>
</head>
<body>
{}
</body>
</html>""".format(
        '\n'.join(css),
        '\n'.join(f'<div>{t}</div>' for t in html)), covered
