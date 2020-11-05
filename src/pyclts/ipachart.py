"""
IPA charts are the most common device to visualize sound inventories.

See also https://en.wikipedia.org/wiki/International_Phonetic_Alphabet_chart
"""
import io
import copy
import pathlib
from xml.etree import ElementTree as et

import attr
from clldutils.misc import lazyproperty

__all__ = ['Segment', 'VowelTrapezoid', 'PulmonicConsonants', 'ipa_charts']


@attr.s
class Segment:
    """
    Bag of attributes controlling display of a segment in an IPA chart.
    """
    sound_bipa = attr.ib(validator=attr.validators.instance_of(str))
    sound_name = attr.ib(validator=attr.validators.instance_of(str))
    label = attr.ib(default=None)
    href = attr.ib(default=None)
    css_class = attr.ib(default=None)
    title = attr.ib(default=None)

    def __attrs_post_init__(self):
        if not self.label:
            self.label = self.sound_bipa
        if not self.title:
            self.title = self.sound_name

    @classmethod
    def from_sound(cls, sound, **kw):
        return cls(sound_bipa=str(sound), sound_name=sound.name, **kw)

    @lazyproperty
    def features(self):
        return set(s.replace('-', '') for s in self.sound_name.split())

    @property
    def link_attrib(self):
        res = {}
        if self.href:
            res['href'] = self.href
        if self.css_class:
            res['class'] = self.css_class
        return res

    @property
    def html_link_attrib(self):
        res = self.link_attrib
        res.update(title=self.title)
        return res


def html_css(id, colorspec=None):
    colorspec = colorspec or {None: ('black', 'solid 1px white')}
    res = ["""\
#{0} a {{text-decoration: none; font-size: smaller;}}
#{0} a {{color: {1};}}
#{0} a {{outline: solid 1px {2};}}
""".format(
        id,
        colorspec.get(None, ('black', None))[0],
        colorspec.get(None, (None, 'solid 1px white'))[1],
    )]
    for cls, (fill, outline) in colorspec.items():
        if cls:
            if fill:
                res.append("#{2} a.{0} text, text svg|a.{0} {{fill: {1};}}".format(cls, fill, id))
            if outline:
                res.append("#{2} a.{0} {{outline: {1};}}".format(cls, outline, id))
    return '\n'.join(res)


def svg_css(colorspec=None):
    """
    :param colorspec:
    :return:
    """
    colorspec = colorspec or {None: ('black', 'solid 1px white')}
    res = ["""\
@namespace svg url(http://www.w3.org/2000/svg);
svg|a:link, svg|a:visited {{cursor: pointer;}}
svg|a text, text svg|a {{fill: {};}}
svg|a {{outline: solid 1px {};}}
svg|a:hover, svg|a:active {{outline: dotted 1px blue;}}
""".format(
        colorspec.get(None, ('black', None))[0],
        colorspec.get(None, (None, 'white'))[1],
    )]
    for cls, (fill, outline) in colorspec.items():
        if cls:
            if fill:
                res.append("svg|a.{0} text, text svg|a.{0} {{fill: {1};}}".format(cls, fill))
            if outline:
                res.append("svg|a.{0} {{outline: {1};}}".format(cls, outline))
                # Unfortunately, there is no outline property in the SVG spec, see
                # https://stackoverflow.com/q/13387851
                # So as a fallback, we add a text-decoration:
                res.append("svg|a.{0} {{text-decoration: underline;}}".format(cls))
                res.append(
                    "svg|a.{0} {{text-decoration-style: {1};}}".format(cls, outline.split()[0]))
                res.append(
                    "svg|a.{0} {{text-decoration-color: {1};}}".format(cls, outline.split()[-1]))

    return '\n'.join(res)


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
        self.slots = {}
        self.exclusive = set()

    @property
    def id(self):
        return self._id or self.__id__

    def iter_slots(self):
        """
        Diagrams must provide a generator of the slots they provide as pairs (features, element),
        where `features` is a set of CLTS features (with NON<feature> specifying absence of a
        feature) and `element` is the ElementTree element where matching segments should be
        appended.
        """
        raise NotImplementedError()

    def fill_slots(self, inventory):
        """
        Assign matching segments to diagram slots.

        :param inventory: `list` of `Segment` instances.
        :return: `set` of inventory indices which have been assigned to slots.
        """
        self.slots = {}
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
            for f in self.slots:
                if f.issubset(features):
                    covered.add(i)
                    self.slots[f][1].append(segment)
                    break
        return covered

    def format_segment(self, element, segment, is_last, is_first):
        """
        Diagrams must provide a method to format segments as ElementTree elements.
        """
        raise NotImplementedError()

    def css(self, colorspec):
        return ''

    def render(self, colorspec=None):
        for e, segments in self.slots.values():
            for i, segment in enumerate(segments, start=1):
                self.format_segment(e, segment, i == len(segments), i == 0)

        self.tree.getroot().attrib['id'] = self.id
        o = io.BytesIO()
        self.tree.write(o)
        return o.getvalue().decode('utf8'), self.css(colorspec)


class PulmonicConsonants(Diagram):
    __id__ = 'pulmonic-consonants'
    __fname__ = 'consonants.html'
    __extend_features__ = frozenset({'consonant'})

    def iter_slots(self):
        for e in self.tree.findall('.//td'):
            if 'class' in e.attrib:
                for attrs in e.attrib['class'].split():
                    attrs = attrs.split('-')
                    for att in attrs:
                        if att.startswith('NON'):
                            self.exclusive.add(att[3:])
                    yield attrs, e

    def format_segment(self, e, segment, is_last, is_first):
        ee = et.SubElement(e, 'a', attrib=segment.html_link_attrib)
        ee.text = segment.label
        if not is_last:
            ee.tail = '\xa0'

    def css(self, colorspec):
        return html_css(self.id, colorspec)


class VowelTrapezoid(Diagram):
    __id__ = 'vowel-trapezoid'
    __fname__ = 'vowels.svg'
    __extend_features__ = frozenset({'vowel'})

    def iter_slots(self):
        ns = {'svg': "http://www.w3.org/2000/svg"}
        et.register_namespace('', ns['svg'])
        for e in self.tree.findall('.//svg:text', ns):
            if 'id' in e.attrib:
                yield e.attrib['id'].split('-'), e

    def format_segment(self, e, segment, is_last, is_first):
        ee = et.SubElement(e, '{http://www.w3.org/2000/svg}a', attrib=segment.link_attrib)
        title = et.SubElement(ee, '{http://www.w3.org/2000/svg}title')
        title.text = segment.title
        ee.text = segment.label
        if not is_last:
            ee.tail = ' '

    def css(self, colorspec):
        return """\
#{0} {{height: 300px; width: 100%; min-width: 800px;}}
#{0} .label {{font-size: 150%;}}
#{0} .glyph {{font-size: 170%;}}
""".format(self.id)

    def render(self, colorspec=None):
        r = self.tree.getroot()
        del r.attrib['width']
        del r.attrib['height']
        style = et.SubElement(r, '{http://www.w3.org/2000/svg}style')
        style.text = svg_css(colorspec)
        res, css = Diagram.render(self)
        return '<figure>{}<figcaption>Vowels</figcaption></figure>'.format(
            res.replace('#666666', '#dddddd')), css


def ipa_charts(inventory, colorspec=None):
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
        css.append(css_)

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
        '\n'.join('<div>{}</div>'.format(t) for t in html)), covered
