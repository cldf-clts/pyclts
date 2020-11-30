"""
Module handles different aspects of inventory comparison.
"""
import attr
from collections import defaultdict, OrderedDict, namedtuple
from pyclts.api import CLTS
import statistics
from pyclts.models import is_valid_sound
from pyclts.cli_util import Table


def reduce_features(sound, clts=None, features=None):
    clts = clts or CLTS().bipa
    features = features or {
        "consonant": ["phonation", "place", "manner"],
        "vowel": ["roundedness", "height", "centrality"],
        "tone": ["start"],
    }
    sound_ = clts[sound] if isinstance(sound, str) else sound
    if sound_.type in ["cluster", "diphthong"]:
        return reduce_features(sound_.from_sound, clts=clts, features=features)
    name = "{} {}".format(
        " ".join(
            [s for s in [sound_.featuredict.get(x) for x in features[sound_.type]] if s]
        ),
        sound_.type,
    )
    if sound_.type != "tone":
        return clts[name]
    return clts["short " + " ".join(name.split(" "))]


@attr.s
class Phoneme:
    """
    Base class for handling sounds.
    """
    grapheme = attr.ib(default=None)
    grapheme_in_source = attr.ib(default=None, repr=False)
    name = attr.ib(default=None)
    type = attr.ib(default=None, repr=False)
    occs = attr.ib(default=None, repr=False)
    attributes = attr.ib(default=None)

    def __len__(self):
        return len(self.occs)

    def __str__(self):
        return self.grapheme


@attr.s
class Inventory:
    id = attr.ib(default=None)
    sounds = attr.ib(default=None, repr=False)
    unknown = attr.ib(default=None, repr=False)
    language = attr.ib(default=None, repr=False)
    bipa = attr.ib(default=None, repr=False)

    @classmethod
    def from_list(cls, *list_of_sounds, language=None, bipa=None):
        bipa = bipa or CLTS().bipa
        unknown = []
        sounds = OrderedDict()
        for itm in list_of_sounds:
            sound = bipa[itm]
            if sound.type in ['unknownsound', 'marker']:
                unknown[str(sound)] = sound
            else:
                sounds[str(sound)] = Phoneme(
                        grapheme=str(sound),
                        grapheme_in_source=sound.grapheme,
                        name=sound.name,
                        type=sound.type,
                        occs=[],
                        attributes=sound)
        return cls(sounds=sounds, bipa=bipa, unknown=unknown, language=language)

    def __len__(self):
        return len(self.sounds)

    @property
    def consonants(self):
        return [s for s in self.sounds.values() if s.type=='consonant']

    @property
    def vowels(self):
        return [s for s in self.sounds.values() if s.type=='vowel']

    @property
    def diphthongs(self):
        return [s for s in self.sounds.values() if s.type=='diphthong']

    @property
    def clusters(self):
        return [s for s in self.sounds.values() if s.type=='clusters']

    @property
    def tones(self):
        return [s for s in self.sounds.values() if s.type=='tone']

    def tabulate(self, format='pipe'):
        table = []
        for sound in self.sounds.values():
            table += [[sound.grapheme, sound.type, sound.name, len(sound)]]
        with Table(namedtuple('args', 'format')(format), 'Grapheme', 'Type', 'Name', 'Frequency') as table_text:
            table_text += table

    def similar(self, other, metric="strict", aspects=None):
        all_aspects = ["consonants", "vowels", "tones"]

        def jac(a, b):
            return len(set(a).intersection(set(b))) / len(set(a).union(set(b)))

        if metric == "strict":
            if not aspects:
                soundsA, soundsB = (
                        {str(sound) for sound in self.sounds},
                        {str(sound) for sound in other.sounds}
                        )
                score = jac(soundsA, soundsB)
            else:
                scores = []
                for aspect in aspects:
                    soundsA, soundsB = (
                            {str(sound) for sound in getattr(self, aspect)},
                            {str(sound) for sound in getattr(other, aspect)}
                            )
                    scores += [jac(soundsA, soundsB)]

                if not scores:
                    score = 0.0
                else:
                    score = statistics.mean(scores)

        elif metric == "approximate":
            # Define internal comparison function
            def _approximate_comp(soundsA, soundsB):
                matches = []
                for sA in soundsA:
                    best, sim = None, 0
                    for sB in soundsB:
                        if sA.similarity(sB) > sim:
                            sim = sA.similarity(sB)
                            best = sB
                    if best:
                        soundsB = [s for s in soundsB if s != best]
                        matches += [sim]
                    else:
                        matches += [0]
                matches += [0 for s in soundsB]

                if matches:
                    return sum(matches) / len(matches)

                return 0.0

            # actual comparison
            if not aspects:
                soundsA, soundsB = {}, {}
                for aspect in all_aspects:
                    soundsA.update(self.sounds[aspect])
                    soundsB.update(other.sounds[aspect])

                soundsA = sorted(soundsA.values(), key=str)
                soundsB = sorted(soundsB.values(), key=str)

                score = _approximate_comp(soundsA, soundsB)
            else:
                scores = []
                for aspect in aspects:
                    soundsA = sorted(self.sounds[aspect].values(), key=str)
                    soundsB = sorted(other.sounds[aspect].values(), key=str)

                    if soundsA or soundsB:
                        scores.append(_approximate_comp(soundsA, soundsB))

                score = statistics.mean(scores)

        return score
