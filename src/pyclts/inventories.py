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
        'consonant': ['phonation', 'place', 'manner'],
        'vowel': ['roundedness', 'height', 'centrality'],
        'tone': ['start']
    }
    sound_ = clts[sound] if isinstance(sound, str) else sound
    if sound_.type in ['cluster', 'diphthong']:
        return reduce_features(sound_.from_sound, clts=clts, features=features)
    name = '{} {}'.format(
        ' '.join([s for s in [sound_.featuredict.get(x) for x in features[sound_.type]] if s]),
        sound_.type)
    if sound_.type != 'tone':
        return clts[name]
    return clts['short ' + ' '.join(name.split(' '))]


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

    def similar(self, other, metric='strict', aspects=None):
        aspects = aspects or ['consonant', 'vowel', 'tone']

        def jac(a, b):
            return len(set(a).intersection(set(b))) / len(set(a).union(set(b)))

        if metric == 'strict':
            score = []
            for aspect in aspects:
                if aspect in self.sounds or aspect in other.sounds:
                    score += [jac(self.sounds[aspect], other.sounds[aspect])]
            return statistics.mean(score)

        if metric == 'approximate':
            score = []
            for aspect in aspects:
                soundsA = list(self.sounds[aspect].values())
                soundsB = list(other.sounds[aspect].values())
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
                    score += [sum(matches) / len(matches)]
            return statistics.mean(score)

        if metric == 'similarity':
            score = []
            for aspect in aspects:
                # Obtain all pairs and compute all similarities; note that we cannot
                # use `itertools` because the sounds end up cast as strings
                simils = {}
                for sound_a in self.sounds[aspect].values():
                    for sound_b in other.sounds[aspect].values():
                        simils[sound_a, sound_b] = sound_a.similarity(sound_b)

                # Look for the highest score and remove the pair; if there is more
                # than one instance with the highest score, just grab the first one
                matched_b = []
                while True:
                    # Leave if there are no simils, including when inventories are empty
                    if not simils:
                        break

                    max_score = max(simils.values())
                    filter = [
                        pair for pair, pair_score in simils.items()
                        if pair_score == max_score][0]

                    score.append(max_score)
                    simils = {
                        pair: pair_score for pair, pair_score in simils.items()
                        if pair[0] != filter[0] and pair[1] != filter[1]
                    }
                    matched_b.append(filter[1])

                # If there are sounds in the `other` inventory that were not matched,
                # add a similarity of 0.0 to each
                num_unmatched = len(other.sounds[aspect]) - len(matched_b)
                score += [0.0] * num_unmatched

            # If there is no `score` (two empty inventories), return zero
            if not score:
                score = [0.0]

            return statistics.mean(score)
