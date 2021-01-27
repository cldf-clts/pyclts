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


class GetAttributeFromSound:
    def __init__(self, attr):
        self.attr = attr

    def __get__(self, obj, objtype=None):
        return getattr(obj.sound, self.attr, None)


@attr.s
class Phoneme:
    """
    Base class for handling sounds.
    """

    grapheme = attr.ib(default=None)
    graphemes_in_source = attr.ib(default=None, repr=False)
    occs = attr.ib(default=None, repr=False)
    sound = attr.ib(default=None)

    type = GetAttributeFromSound("type")
    name = GetAttributeFromSound("name")
    featureset = GetAttributeFromSound("featureset")

    def __len__(self):
        return len(self.occs)

    def __str__(self):
        return self.grapheme

    def similarity(self, other):
        if self.type not in ["marker", "unknownsound"]:
            return self.sound.similarity(other.sound)
        if self == other:
            return 1
        return 0


class GetSubInventoryByType:
    def __init__(self, types):
        def select_sounds(inventory):
            return OrderedDict(
                [(k, v) for k, v in inventory.items() if v.type in types]
            )

        self.select_sounds = select_sounds

    def __get__(self, obj, objtype=None):
        return self.select_sounds(obj.sounds)


class GetSubInventoryByProperty(GetSubInventoryByType):
    def __init__(self, types, properties):
        GetSubInventoryByType.__init__(self, types)
        self.properties = properties

    def __get__(self, obj, objtype=None):
        out = OrderedDict()
        sounds = self.select_sounds(obj.sounds)
        for k, v in sounds.items():
            stripped = obj.ts.features.get(
                frozenset([s for s in v.featureset if s not in self.properties])
            )
            if str(stripped) != str(v) and str(stripped) not in sounds:
                out[k] = v
            elif str(stripped) == str(v):
                out[k] = v
        return out


@attr.s
class Inventory:
    id = attr.ib(default=None)
    language = attr.ib(default=None)
    sounds = attr.ib(default=None, repr=False)
    ts = attr.ib(default=None, repr=False)

    consonants = GetSubInventoryByType(["consonant"])
    consonants_by_quality = GetSubInventoryByProperty(
        ["consonant"], ["long", "ultra-long", "mid-long", "ultra-short"]
    )
    consonant_sounds = GetSubInventoryByType(["consonant", "cluster"])
    vowels = GetSubInventoryByType(["vowel"])
    vowels_by_quality = GetSubInventoryByProperty(
        ["vowel"], ["long", "ultra-long", "mid-long", "ultra-short"]
    )
    vowel_sounds = GetSubInventoryByType(["vowel", "diphthong"])
    segments = GetSubInventoryByType(["consonant", "vowel", "cluster", "diphthong"])
    tones = GetSubInventoryByType(["tone"])
    markers = GetSubInventoryByType(["marker"])
    clusters = GetSubInventoryByType(["cluster"])
    diphthongs = GetSubInventoryByType(["diphthong"])
    unknownsounds = GetSubInventoryByType(["unknownsound"])

    @classmethod
    def from_list(cls, *list_of_sounds, id=None, language=None, ts=None):
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
                    sound=sound,
                )
        return cls(sounds=sounds, ts=ts, language=language, id=id)

    def __len__(self):
        return len(self.sounds)

    def tabulate(self, format="pipe", types=None):
        types = types or ["sounds"]
        table = []
        for t in types:
            for sound in getattr(self, t).values():
                table += [[sound.grapheme, sound.type, sound.name, len(sound)]]
        with Table(
            namedtuple("args", "format")(format),
            "Grapheme",
            "Type",
            "Name",
            "Frequency",
        ) as table_text:
            table_text += table

    def strict_similarity(self, other, aspects=None):
        aspects = aspects or ["sounds"]
        scores = []
        for aspect in aspects:
            soundsA, soundsB = (
                {sound for sound in getattr(self, aspect)},
                {sound for sound in getattr(other, aspect)},
            )
            if soundsA or soundsB:
                scores += [jaccard(soundsA, soundsB)]
        if not scores:
            return 0
        return statistics.mean(scores)

    def approximate_similarity(self, other, aspects=None):
        aspects = aspects or ["sounds"]

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
                getattr(other, aspect).values(),
            )
            if soundsA and soundsB:
                scores += [
                    statistics.mean(
                        [approximate(soundsA, soundsB), approximate(soundsB, soundsA)]
                    )
                ]
            elif soundsA or soundsB:
                scores += [0]
        if not scores:
            return 0
        return statistics.mean(scores)
