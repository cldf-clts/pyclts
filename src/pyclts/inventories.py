"""
Module handles different aspects of inventory comparison.
"""
import argparse
import statistics
import collections
from collections.abc import Iterable
import dataclasses
from typing import Optional, Union, Literal

from clldutils.clilib import Table

from pyclts.api import CLTS
from pyclts.models import (
    Sound, Symbol, COMPLEX_SOUNDS, Tone, Marker, UnknownSound, BaseSoundclassType)
from pyclts.datatypes import TranscriptionSystem, FeatureNameType
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
    if sound_.type() in COMPLEX_SOUNDS:
        return reduce_features(sound_.from_sound, ts=ts, features=features)

    fs = " ".join(s for s in [sound_.featuredict.get(x) for x in features[sound_.type()]] if s)
    name = f"{fs} {sound_.type()}"
    if not isinstance(sound_, Tone):
        return ts[name]
    return ts["short " + " ".join(name.split(" "))]


@dataclasses.dataclass
class Phoneme:
    """
    Base class for handling sounds.
    """

    grapheme: str = None
    graphemes_in_source: list[str] = dataclasses.field(default_factory=list, repr=False)
    occs: list = dataclasses.field(default_factory=list, repr=False)
    sound: Optional[Sound] = None

    @property
    def name(self):
        """Facade for the sound attribute."""
        return self.sound.name

    @property
    def featureset(self):
        """Facade for the sound attribute."""
        return self.sound.featureset

    def __len__(self):
        return len(self.occs)

    def __str__(self):
        return self.grapheme

    def similarity(self, other) -> float:
        """Similarity of phonemes is largely computed as similarity of underlying sounds."""
        if not isinstance(self.sound, (Marker, UnknownSound)):
            return self.sound.similarity(other.sound)
        if self == other:
            return 1
        return 0


PhonemeDictType = dict[str, Phoneme]


def _subinventory_by_type(sounds: Iterable[dict[str, Sound]], types: list[str]) -> PhonemeDictType:
    return collections.OrderedDict(
        [(k, v) for k, v in sounds.items() if v.sound.type() in types])


def _subinventory_by_ignored_features(
        sounds: Iterable[dict[str, Sound]],
        types: list[str],
        features_to_sound: dict[frozenset[str], Sound],
        properties: list[str],
) -> PhonemeDictType:
    out = collections.OrderedDict()
    for k, v in _subinventory_by_type(sounds, types).items():
        stripped = features_to_sound.get(
            frozenset([s for s in v.featureset if s not in properties]))
        if str(stripped) != str(v) and str(stripped) not in sounds:
            out[k] = v
        elif str(stripped) == str(v):
            out[k] = v
    return out


# The PhonemeDictType-valued attributes of Inventory.
AspectType = Literal[
    'sounds',
    'consonants', 'consonants_by_quality', 'consonant_sounds',
    'vowels', 'vowels_by_quality', 'vowel_sounds',
    'segments', 'tones', 'markers', 'clusters', 'diphthongs', 'unknownsounds',
]


@dataclasses.dataclass
class Inventory:  # pylint: disable=too-many-instance-attributes
    """A phoneme inventory."""
    id: Optional[str]
    language: Optional[str]
    ts: Optional[TranscriptionSystem] = dataclasses.field(repr=False)

    sounds: PhonemeDictType = dataclasses.field(repr=False)
    consonants: PhonemeDictType = dataclasses.field(repr=False)
    # Consonants, ignoring differences just in length.
    consonants_by_quality: PhonemeDictType = dataclasses.field(repr=False)
    consonant_sounds: PhonemeDictType = dataclasses.field(repr=False)
    vowels: PhonemeDictType = dataclasses.field(repr=False)
    # Vowels, ignoring differences just in length.
    vowels_by_quality: PhonemeDictType = dataclasses.field(repr=False)
    vowel_sounds: PhonemeDictType = dataclasses.field(repr=False)
    segments: PhonemeDictType = dataclasses.field(repr=False)
    tones: PhonemeDictType = dataclasses.field(repr=False)
    markers: PhonemeDictType = dataclasses.field(repr=False)
    clusters: PhonemeDictType = dataclasses.field(repr=False)
    diphthongs: PhonemeDictType = dataclasses.field(repr=False)
    unknownsounds: PhonemeDictType = dataclasses.field(repr=False)

    @classmethod
    def from_list(
            cls,
            *list_of_sounds: Union[str, Sound],
            id: Optional[str] = None,  # pylint: disable=W0622
            language: Optional[str] = None,
            ts: Optional[TranscriptionSystem] = None
    ) -> 'Inventory':
        """Initialize an inventory from a list of sounds."""
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
        kw = dict(  # pylint: disable=R1735
            consonants=_subinventory_by_type(sounds, ["consonant"]),
            # Consonants, ignoring differences just in length.
            consonants_by_quality=_subinventory_by_ignored_features(
                sounds,
                ["consonant"],
                ts.features_to_sound,
                ["long", "ultra-long", "mid-long", "ultra-short"]),
            consonant_sounds=_subinventory_by_type(sounds, ["consonant", "cluster"]),
            vowels=_subinventory_by_type(sounds, ["vowel"]),
            # Vowels, ignoring differences just in length.
            vowels_by_quality=_subinventory_by_ignored_features(
                sounds,
                ["vowel"],
                ts.features_to_sound,
                ["long", "ultra-long", "mid-long", "ultra-short"]),
            vowel_sounds=_subinventory_by_type(sounds, ["vowel", "diphthong"]),
            segments=_subinventory_by_type(
                sounds, ["consonant", "vowel", "cluster", "diphthong"]),
            tones=_subinventory_by_type(sounds, ["tone"]),
            markers=_subinventory_by_type(sounds, ["marker"]),
            clusters=_subinventory_by_type(sounds, ["cluster"]),
            diphthongs=_subinventory_by_type(sounds, ["diphthong"]),
            unknownsounds=_subinventory_by_type(sounds, ["unknownsound"]),
        )
        return cls(sounds=sounds, ts=ts, language=language, id=id, **kw)

    def __len__(self):
        return len(self.sounds)

    def tabulate(
            self,
            format: str = "pipe",  # pylint: disable=W0622
            types: Optional[list[AspectType]] = None):
        """Render the inventory as table of graphemes."""
        types = types or ["sounds"]
        table = []
        for t in types:
            for sound in getattr(self, t).values():
                table.append([sound.grapheme, sound.sound.type(), sound.name, len(sound)])
        with Table(
            argparse.Namespace(format=format),
            "Grapheme",
            "Type",
            "Name",
            "Frequency",
        ) as table_text:
            table_text += table

    def strict_similarity(
            self,
            other: 'Inventory',
            aspects: Optional[list[AspectType]] = None,
    ) -> float:
        """Compute strict similarity between two inventories."""
        scores = []
        for aspect in aspects or ["sounds"]:
            snds_a = set(getattr(self, aspect))
            snds_b = set(getattr(other, aspect))
            if snds_a or snds_b:
                scores.append(jaccard(snds_a, snds_b))
        return statistics.mean(scores) if scores else 0

    def approximate_similarity(
            self,
            other: 'Inventory',
            aspects: Optional[list[AspectType]] = None,
    ) -> float:
        """Compute the approximate similarity between two inventories."""
        def _approximate(snds_a, snds_b) -> float:
            matches = []
            for snd_a in snds_a:
                best_match, best_sim = None, 0
                for snd_b in snds_b:
                    current_sim = snd_a.similarity(snd_b)
                    if current_sim > best_sim:
                        best_match = snd_b
                        best_sim = current_sim
                if best_match is not None:
                    matches.append(best_sim)
                    snds_b = [s for s in snds_b if s != best_match]
            matches.extend([0 for _ in snds_b])
            return statistics.mean(matches)

        scores = []
        for aspect in aspects or ["sounds"]:
            snds_a = getattr(self, aspect).values()
            snds_b = getattr(other, aspect).values()
            if snds_a and snds_b:
                scores.append(
                    statistics.mean([
                        _approximate(snds_a, snds_b),
                        _approximate(snds_b, snds_a)]))  # pylint: disable=W1114
            elif snds_a or snds_b:
                scores.append(0)
        return statistics.mean(scores) if scores else 0
