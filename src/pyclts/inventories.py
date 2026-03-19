"""
Module handles different aspects of inventory comparison.
"""
import argparse
import statistics
import collections
import dataclasses
from typing import Optional, Union

from clldutils.clilib import Table

from pyclts.api import CLTS
from pyclts.models import Sound, Symbol
from pyclts.transcriptionsystem import TranscriptionSystem, BaseSoundclassType, FeatureNameType
from pyclts.util import jaccard
from pyclts.features import ConsonantFeatures, VowelFeatures, ToneFeatures


def _iter_reduced_features(cls):
    for f in cls.fields():
        if f.metadata.get('reduced'):
            yield f.name


def reduce_features(
        sound: Union[str, Sound],
        ts: Optional[TranscriptionSystem] = None,
        features: Optional[dict[BaseSoundclassType, list[FeatureNameType]]] = None,
) -> Union[Symbol, Sound]:
    """Extract subset of features from `sound` and return a sound having these features."""
    ts = ts or CLTS().bipa

    if not features:  # Get the default reduced set of features from the pyclts feature system.
        features = {
            cls.__name__.replace('Features', '').lower():
                list(_iter_reduced_features(cls))
            for cls in [ConsonantFeatures, VowelFeatures, ToneFeatures]}

    sound_ = ts[sound] if isinstance(sound, str) else sound
    if sound_.type in ["cluster", "diphthong"]:
        return reduce_features(sound_.from_sound, ts=ts, features=features)

    fs = " ".join(s for s in [sound_.featuredict.get(x) for x in features[sound_.type]] if s)
    name = f"{fs} {sound_.type}"
    if sound_.type != "tone":
        return ts[name]
    return ts["short " + " ".join(name.split(" "))]


class GetAttributeFromSound:
    def __init__(self, attr):
        self.attr = attr

    def __get__(self, obj, objtype=None):
        return getattr(obj.sound, self.attr, None)


@dataclasses.dataclass
class Phoneme:
    """
    Base class for handling sounds.
    """

    grapheme: str = None
    graphemes_in_source: list[str] = dataclasses.field(default_factory=list, repr=False)
    occs: list = dataclasses.field(default_factory=list, repr=False)
    sound: Optional[Sound] = None

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
            return collections.OrderedDict(
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
        out = collections.OrderedDict()
        sounds = self.select_sounds(obj.sounds)
        for k, v in sounds.items():
            stripped = obj.ts.features_to_sound.get(
                frozenset([s for s in v.featureset if s not in self.properties])
            )
            if str(stripped) != str(v) and str(stripped) not in sounds:
                out[k] = v
            elif str(stripped) == str(v):
                out[k] = v
        return out


@dataclasses.dataclass
class Inventory:
    id: Optional[str] = None
    language: Optional[str] = None
    sounds: dict[str, Phoneme] = dataclasses.field(default_factory=dict, repr=False)
    ts: Optional[TranscriptionSystem] = dataclasses.field(default=None, repr=False)

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
        sounds = collections.OrderedDict()
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
            argparse.Namespace(format=format),
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
            snds_a = {sound for sound in getattr(self, aspect)}
            snds_b = {sound for sound in getattr(other, aspect)}
            if snds_a or snds_b:
                scores += [jaccard(snds_a, snds_b)]
        return statistics.mean(scores) if scores else 0

    def approximate_similarity(self, other, aspects=None):
        aspects = aspects or ["sounds"]

        def approximate(snds_a, snds_b):
            matches = []
            for snd_a in snds_a:
                best_match, best_sim = None, 0
                for snd_b in snds_b:
                    current_sim = snd_a.similarity(snd_b)
                    if current_sim > best_sim:
                        best_match = snd_b
                        best_sim = current_sim
                if best_match is not None:
                    matches += [best_sim]
                    snds_b = [s for s in snds_b if s != best_match]
            matches += [0 for _ in snds_b]
            return statistics.mean(matches)

        scores = []
        for aspect in aspects:
            snds_a = getattr(self, aspect).values()
            snds_b = getattr(other, aspect).values()
            if snds_a and snds_b:
                scores.append(
                    statistics.mean([approximate(snds_a, snds_b), approximate(snds_b, snds_a)]))
            elif snds_a or snds_b:
                scores.append(0)
        return statistics.mean(scores) if scores else 0
