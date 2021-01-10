"""
Module handles different aspects of inventory comparison.
"""
import attr
from collections import OrderedDict, namedtuple
from pyclts.api import CLTS
import statistics
from pyclts.cli_util import Table
from pyclts.util import jaccard


def reduce_features(sound, ts=None, features=None):
    ts = ts or CLTS().bipa
    features = features or {
        "consonant": ["phonation", "place", "manner"],
        "vowel": ["roundedness", "height", "centrality"],
        "tone": ["start"],
    }
    sound_ = ts[sound] if isinstance(sound, str) else sound
    if sound_.type in ["cluster", "diphthong"]:
        return reduce_features(sound_.from_sound, ts=ts, features=features)
    name = "{} {}".format(
        " ".join(
            [s for s in [sound_.featuredict.get(x) for x in features[sound_.type]] if s]
        ),
        sound_.type,
    )
    if sound_.type != "tone":
        return ts[name]
    return ts["short " + " ".join(name.split(" "))]


@attr.s
class Phoneme:
    """
    Base class for handling sounds.
    """
    grapheme = attr.ib(default=None)
    graphemes_in_source = attr.ib(default=None, repr=False)
    occs = attr.ib(default=None, repr=False)
    sound = attr.ib(default=None)
    
    @property
    def type(self):
        return self.sound.type

    @property
    def name(self):
        return self.sound.name

    @property
    def featureset(self):
        if hasattr(self.sound, "featureset"):
            return self.sound.featureset
        else:
            return frozenset()

    def __len__(self):
        return len(self.occs)

    def __str__(self):
        return self.grapheme

    def similarity(self, other):
        if self.type not in ['marker', 'unknownsound']:
            return self.sound.similarity(other.sound)
        if self == other:
            return 1
        return 0


def select_by_type(*types):
    def wrapper(function):
        def select_sounds(inventory):
            return OrderedDict([(k, v) for k, v in function(inventory).items() if v.type in
                types])
        return select_sounds
    return wrapper


def filter_by_property(*properties):
    def wrapper(function):
        def select_sounds(inventory):
            # manipulate the properties to strip off the property from the
            # items
            out = OrderedDict()
            sounds = function(inventory)
            for k, v in sounds.items():
                stripped = inventory.ts.features.get(
                        frozenset([s for s in v.featureset if s not in properties]))
                if str(stripped) != str(v) and str(stripped) not in sounds:
                    out[k] = v
                elif str(stripped) == str(v):
                    out[k] = v
            return out
        return select_sounds
    return wrapper


@attr.s
class Inventory:
    id = attr.ib(default=None)
    sounds = attr.ib(default=None, repr=False)
    language = attr.ib(default=None, repr=False)
    ts = attr.ib(default=None, repr=False)

    @classmethod
    def from_list(cls, *list_of_sounds, language=None, ts=None):
        ts = ts or CLTS().bipa
        sounds = OrderedDict()
        for itm in list_of_sounds:
            sound = ts[itm]
            try:
                sounds[str(sound)].graphemes_in_source.append(itm)
            except KeyError:
                sounds[str(sound)] = Phoneme(
                    grapheme=str(sound),
                    graphemes_in_source=[sound.grapheme],
                    occs=[],
                    sound=sound)
        return cls(sounds=sounds, ts=ts, language=language)

    def __len__(self):
        return len(self.sounds)

    @property
    @select_by_type("consonant")
    def consonants(self):
        return self.sounds

    @property
    @select_by_type("marker")
    def markers(self):
        return self.sounds

    @property
    @select_by_type("vowel", "diphthong")
    def vocoids(self):
        return self.sounds

    @property
    @filter_by_property("long", "mid-long", "ultra-short", "ultra-long")
    @select_by_type("vowel")
    def vowels_by_quality(self):
        return self.sounds

    @property
    @filter_by_property("long", "mid-long", "ultra-short", "ultra-long")
    @select_by_type("consonant")
    def consonants_by_quality(self):
        return self.sounds

    @property
    @select_by_type("consonant", "cluster")
    def consonantoids(self):
        return self.sounds

    @property
    @select_by_type("consonant", "vowel", "diphthong", "cluster")
    def segmentals(self):
        return self.sounds

    @property
    @select_by_type("unknownsound")
    def unknownsounds(self):
        return self.sounds

    @property
    @select_by_type("vowel")
    def vowels(self):
        return self.sounds

    @property
    @select_by_type("diphthong")
    def diphthongs(self):
        return self.sounds

    @property
    @select_by_type("cluster")
    def clusters(self):
        return self.sounds

    @property
    @select_by_type("tone")
    def tones(self):
        return self.sounds

    def tabulate(self, format='pipe', types=None):
        types = types or ['sounds']
        table = []
        for t in types:
            for sound in getattr(self, t).values():
                table += [[sound.grapheme, sound.type, sound.name, len(sound)]]
        with Table(
                namedtuple('args', 'format')(format),
                'Grapheme', 'Type', 'Name', 'Frequency') as table_text:
            table_text += table

    def strict_similarity(self, other, aspects=None):
        aspects = aspects or ['sounds']
        scores = []
        for aspect in aspects:
            soundsA, soundsB = (
                {sound for sound in getattr(self, aspect)},
                {sound for sound in getattr(other, aspect)})
            if soundsA or soundsB:
                scores += [jaccard(soundsA, soundsB)]
        if not scores:
            return 0
        return statistics.mean(scores)

    def approximate_similarity(self, other, aspects=None):
        aspects = aspects or ['sounds']

        def approximate(soundsA, soundsB):
            matches = []
            for soundA in soundsA:
                best_match, best_sim = None, 0
                for soundB in soundsB:
                    current_sim = soundA.similarity(soundB)
                    if current_sim > best_sim:
                        best_match = soundB
                        best_sim = current_sim
                if best_match is not None:
                    matches += [best_sim]
                    soundsB = [s for s in soundsB if s != best_match]
            matches += [0 for s in soundsB]
            return statistics.mean(matches)

        scores = []
        for aspect in aspects:
            soundsA, soundsB = (
                getattr(self, aspect).values(),
                getattr(other, aspect).values())
            if soundsA and soundsB:
                scores += [statistics.mean([
                    approximate(soundsA, soundsB),
                    approximate(soundsB, soundsA)])]
            elif soundsA or soundsB:
                scores += [0]
        if not scores:
            return 0
        return statistics.mean(scores)
