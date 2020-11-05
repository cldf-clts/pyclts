"""
Module handles different aspects of inventory comparison.
"""
import attr
from collections import defaultdict
from pyclts.api import CLTS
import statistics


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
class Inventory:
    sounds = attr.ib()
    clts = attr.ib(default=None)

    @classmethod
    def from_list(cls, *list_of_sounds, clts=None):
        clts = clts or CLTS().bipa

        sounds = defaultdict(dict)
        for itm in list_of_sounds:
            sound = clts[itm]
            sounds[sound.type][sound.s] = sound
            for ft, val in sound.featuredict.items():
                if val:
                    sounds[val][sound.s] = sound
        return cls(sounds=sounds, clts=clts)

    def similar(self, other, metric="strict", aspects=None):
        all_aspects = ["consonant", "vowel", "tone"]

        def jac(a, b):
            return len(set(a).intersection(set(b))) / len(set(a).union(set(b)))

        if metric == "strict":
            if not aspects:
                soundsA, soundsB = {}, {}
                for aspect in all_aspects:
                    soundsA.update(self.sounds[aspect])
                    soundsB.update(other.sounds[aspect])

                score = jac(soundsA, soundsB)
            else:
                scores = []
                for aspect in aspects:
                    if aspect in self.sounds or aspect in other.sounds:
                        scores += [jac(self.sounds[aspect], other.sounds[aspect])]

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
