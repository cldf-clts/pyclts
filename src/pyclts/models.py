import functools
import unicodedata

import attr
from clldutils.misc import nfilter

from pyclts.util import norm, jaccard

__all__ = [
    'is_valid_sound',
    'Symbol',
    'Sound',
    'Consonant',
    'Vowel',
    'Tone',
    'Marker',
    'Diphthong',
    'Cluster',
    'UnknownSound']
EXCLUDE_FEATURES = [
    'apical',
    'laminal',
    'ejective',
    'with-falling_tone',
    'with-extra-low_tone',
    'with-extra-high_tone',
    'with-falling_tone',
    'with-low_tone',
    'with-global_fall',
    'with-global_rise',
    'with-high_tone',
    'with-mid_tone',
    'with-rising_tone',
    'with-upstep'
]
# Disable cmp in a backwards and forwards compatible way:
cmp_off = {"eq" if getattr(attr, "__version_info__", (0,)) >= (19, 2) else "cmp": False}


def is_valid_sound(sound, ts):
    """Check the consistency of a given transcription system conversino"""
    if isinstance(sound, (Marker, UnknownSound)):
        return False
    s1 = ts[sound.name]
    s2 = ts[sound.s]
    return s1.name == s2.name and s1.s == s2.s


@attr.s(**cmp_off)
class Symbol(object):
    ts = attr.ib()
    grapheme = attr.ib()
    source = attr.ib(default=None)
    generated = attr.ib(default=False, validator=attr.validators.instance_of(bool))
    note = attr.ib(default=None)

    @functools.cached_property
    def type(self):
        return self.__class__.__name__.lower()

    def __str__(self):
        return self.grapheme

    def __eq__(self, other):
        """
        In the absence of features, we consider symbols equal, if they belong to the same
        system and are represented by the same grapheme.
        """
        return self.ts.id == other.ts.id and self.grapheme == other.grapheme

    @property
    def name(self):
        return None

    @property
    def uname(self):
        "Return unicode name(s) for a character set."
        try:
            return ' / '.join(unicodedata.name(ss) for ss in str(self))
        except TypeError:
            return '-'
        except ValueError:
            return '?'

    @property
    def codepoints(self):
        "Return unicode codepoint(s) for a grapheme."
        return ' '.join('U+' + ('000' + hex(ord(x))[2:])[-4:] for x in str(self))


@attr.s(**cmp_off)
class UnknownSound(Symbol):
    pass


@attr.s(repr=False, **cmp_off)
class Sound(Symbol):
    """
    Sound object stores basic features of the individual sound objects.
    """
    base = attr.ib(default=None)
    alias = attr.ib(default=None)
    normalized = attr.ib(default=None)
    unknown = attr.ib(default=None)
    stress = attr.ib(default=None)

    _name_order = []
    _write_order = dict(pre=[], post=[])

    def __eq__(self, other):
        if isinstance(other, Sound):
            return self.name == other.name
        return False

    def __repr__(self):
        return '<{0}.{1}: {2}>'.format(
            self.__module__, self.__class__.__name__, self.name)

    def __add__(self, other):
        return str(self) + str(other)

    def __hash__(self):
        return hash(self.name)

    @property
    def s(self):
        return str(self)

    def _features(self):
        return nfilter(getattr(self, p, None) for p in self._name_order)

    @property
    def featuredict(self):
        return {f: getattr(self, f, None) for f in self._name_order}

    @property
    def featureset(self):
        return frozenset(self._features() + [self.type])

    def similarity(self, other):
        return jaccard(self.featureset, other.featureset)

    def __str__(self):
        """
        Return the reference representation of the sound.

        Note
        ----
        We first try to return the non-alias value in our data. If this fails,
        we create the sound based on it's feature representation.
        """
        # generated sounds need to be re-produced for double-checking
        if not self.generated:
            if not self.alias and self.grapheme in self.ts.sounds:
                return self.grapheme
            elif self.alias and self.featureset in self.ts.features:
                return str(self.ts.features[self.featureset])
            # this can usually not happen, as we catch these errors when loading a ts!
            raise ValueError(
                'Orphaned alias {0}'.format(self.grapheme))  # pragma: no cover

        # search for best base-string
        elements = [f for f in self._features() if f not in EXCLUDE_FEATURES] + [self.type]
        base_str = self.base or '<?>'
        base_graphemes = []
        while elements:
            base = self.ts.features.get(frozenset(elements))
            if base:
                base_graphemes.append(base.grapheme)
            elements.pop(0)
        base_str = base_graphemes[-1] if base_graphemes else base_str or '<?>'
        base_vals = {
            self.ts._feature_values[elm] for elm in
            self.ts.sounds[base_str].name.split(' ')[:-1]} if \
            base_str != '<?>' else {}
        out = []
        for p in self._write_order['pre']:
            if p not in base_vals and getattr(self, p, '') in self._features():
                out.append(
                    norm(self.ts.features[self.type].get(getattr(self, p, ''), '<!>')))
        out.append(base_str)
        for p in self._write_order['post']:
            if p not in base_vals and getattr(self, p, '') in self._features():
                out.append(
                    norm(self.ts.features[self.type].get(getattr(self, p, ''), '<!>')))
        return ''.join(out)

    @property
    def name(self):
        return ' '.join([f or '' for f in self._features()] + [self.type])

    @property
    def table(self):
        """Returns the tabular representation of the sound as given in our data
        """
        tbl = []
        features = [
            f for f in self._name_order if f not in self.ts.columns[self.type]]
        # make sure to mark generated sounds
        if self.generated and self.s != self.source:
            tbl += [str(self) + ' | ' + self.source]
        else:
            tbl += [str(self)]
        for name in self.ts.columns[self.type][1:]:
            if name != 'extra' and name != 'alias':
                tbl += [getattr(self, name) or '']
            elif name == 'alias':
                tbl += ['+' if getattr(self, name) else '']
            else:
                bundle = []
                for f in features:
                    val = getattr(self, f)
                    if val:
                        bundle += ['{0}:{1}'.format(f, val)]
                tbl += [','.join(bundle)]
        return tbl

    @property
    def symbols(self):
        """Returns all unicode sounds separated by the empty sound marker.
        """
        return ' '.join(['◌' + s for s in self.s])


@attr.s(**cmp_off)
class Marker(Symbol):
    alias = attr.ib(default=None)
    feature = attr.ib(default=None)
    value = attr.ib(default=None)
    unknown = attr.ib(default=None)

    @property
    def name(self):
        return self.grapheme

    @property
    def featureset(self):
        return frozenset([self.grapheme, self.type])


@attr.s(repr=False, **cmp_off)
class Consonant(Sound):

    # features follow basic information about IPA from various sources, they
    # are potentially not yet exhaustive and should be updated at some point
    manner = attr.ib(default=None)
    place = attr.ib(default=None)
    aspiration = attr.ib(default=None)
    labialization = attr.ib(default=None)
    palatalization = attr.ib(default=None)
    preceding = attr.ib(default=None)
    velarization = attr.ib(default=None)
    duration = attr.ib(default=None)
    phonation = attr.ib(default=None)
    release = attr.ib(default=None)
    syllabicity = attr.ib(default=None)
    nasalization = attr.ib(default=None)
    glottalization = attr.ib(default=None)
    pharyngealization = attr.ib(default=None)
    ejection = attr.ib(default=None)
    voicing = attr.ib(default=None)
    breathiness = attr.ib(default=None)
    creakiness = attr.ib(default=None)
    airstream = attr.ib(default=None)
    laminality = attr.ib(default=None)
    articulation = attr.ib(default=None)
    raising = attr.ib(default=None)
    relative_articulation = attr.ib(default=None)
    friction = attr.ib(default=None)
    tongue_root = attr.ib(default=None)

    # write order determines how consonants are written according to their
    # features, so this normalizes the order of diacritics preceding and
    # following the base part of the consonant
    _write_order = dict(
        pre=['preceding'],
        post=[
            'raising',
            'relative_articulation',
            'laminality',
            'creakiness',
            'tongue_root',
            'phonation',
            'ejection',
            'syllabicity',
            'voicing',
            'articulation',
            'nasalization',
            'release',
            'palatalization',
            'labialization',
            'velarization',
            'pharyngealization',
            'glottalization',
            'breathiness',
            'aspiration',
            'friction',
            'duration',
        ],
    )

    _name_order = [
        'raising',
        'relative_articulation',
        'friction',
        'articulation',
        'preceding',
        'syllabicity',
        'nasalization',
        'palatalization',
        'labialization',
        'velarization',
        'pharyngealization',
        'glottalization',
        'aspiration',
        'duration',
        'release',
        'voicing',
        'creakiness',
        'breathiness',
        'phonation',
        'laminality',
        'tongue_root',
        'place',
        'ejection',
        'airstream',
        'manner',
    ]


@attr.s(repr=False, **cmp_off)
class ComplexSound(Sound):
    from_sound = attr.ib(default=None)
    to_sound = attr.ib(default=None)

    def __str__(self):
        return str(self.from_sound) + str(self.to_sound)

    @property
    def name(self):
        n1 = ' '.join(self.from_sound.name.split(' ')[:-1])
        n2 = ' '.join(self.to_sound.name.split(' ')[:-1])
        return 'from ' + n1 + ' to ' + n2 + ' ' + self.type

    def _features(self):
        res = ['from_' + p for p in nfilter(
            getattr(self.from_sound, p, None) for p in self.from_sound._name_order)]
        res.extend([
            'to_' + p for p in nfilter(
                getattr(self.to_sound, p, None) for p in self.to_sound._name_order)])
        if self.from_sound.type == "vowel":
            res.append("diphthong")
        if self.from_sound.type == "consonant":
            res.append("cluster")
        return res

    @property
    def featuredict(self):
        res = {'from_' + p: getattr(self.from_sound, p, None) for p in self.from_sound._name_order}
        res.update({'to_' + p: getattr(self.to_sound, p, None) for p in self.to_sound._name_order})
        return res

    @classmethod
    def from_sounds(cls, source, sound1, sound2, ts):
        return cls(
            source=source,
            grapheme=sound1.grapheme + sound2.grapheme,
            from_sound=sound1,
            to_sound=sound2,
            ts=ts,
            generated=True,
            stress=sound1.stress or sound2.stress
        )

    @property
    def table(self):
        """Overwrite the table attribute for complex sounds"""
        return [self.grapheme, self.from_sound.name, self.to_sound.name]


@attr.s(repr=False, **cmp_off)
class Cluster(ComplexSound):
    """
    A cluster of two consonants whose manner is either plosive or implosive.

    Notes
    -----
    To keep the search space low and to avoid that users start defining too
    invalid sound clusters, we restrict the ```manner``` attribute of the two
    sounds to ```plosive``` and ```implosive```.
    """


@attr.s(repr=False, **cmp_off)
class Vowel(Sound):
    roundedness = attr.ib(default=None)
    height = attr.ib(default=None)
    nasalization = attr.ib(default=None)
    friction = attr.ib(default=None)
    duration = attr.ib(default=None)
    voicing = attr.ib(default=None)
    breathiness = attr.ib(default=None)
    creakiness = attr.ib(default=None)
    release = attr.ib(default=None)
    syllabicity = attr.ib(default=None)
    pharyngealization = attr.ib(default=None)
    rhotacization = attr.ib(default=None)
    centrality = attr.ib(default=None)
    glottalization = attr.ib(default=None)
    velarization = attr.ib(default=None)
    relative_articulation = attr.ib(default=None)
    tone = attr.ib(default=None)
    raising = attr.ib(default=None)
    rounding = attr.ib(default=None)
    tongue_root = attr.ib(default=None)
    articulation = attr.ib(default=None)  # compare
    # https://en.wikipedia.org/wiki/Faucalized_voice

    _write_order = dict(
        pre=[],
        post=[
            'tongue_root',
            'raising',
            'centrality',
            'rounding',
            'voicing',
            'breathiness',
            'creakiness',
            'syllabicity',
            'friction',
            'relative_articulation',
            'nasalization',
            'tone',
            'articulation',
            'rhotacization',
            'pharyngealization',
            'glottalization',
            'velarization',
            'duration'])
    _name_order = [
        'duration', 'rhotacization', 'pharyngealization',
        'glottalization', 'velarization', 'syllabicity',
        'relative_articulation',
        'tongue_root', 'raising', 'rounding',
        'articulation', 'nasalization', 'voicing', 'creakiness',
        'breathiness', 'roundedness', 'height', 'friction', 'centrality',
        'tone']


@attr.s(repr=False, **cmp_off)
class Diphthong(ComplexSound):
    """
    A dipthong consists of two vowels.
    """


@attr.s(repr=False, **cmp_off)
class Tone(Sound):
    contour = attr.ib(default=None)
    start = attr.ib(default=None)
    middle = attr.ib(default=None)
    end = attr.ib(default=None)

    _name_order = ['contour', 'start', 'middle', 'end']
