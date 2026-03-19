"""
Transcription System module for consistent IPA handling.
========================================================

"""
import re
from typing import Literal, get_args, Union

from csvw import TableGroup

from pyclts.models import fieldnames
from pyclts.util import nfd, norm, EMPTY, itertable, TranscriptionBase
from pyclts.models import (
    Sound, UnknownSound, Cluster, Diphthong, Vowel, Consonant, Tone, Marker, Symbol)

SoundsByFeatures = dict[frozenset, Sound]
BaseSoundclassType = Literal['consonant', 'vowel', 'tone']
BaseSoundclassOrMarkerType = Literal['consonant', 'vowel', 'tone', 'marker']
BaseSoundclassMappingType = dict[BaseSoundclassType, dict[str, str]]

COMPLEX_SOUNDS = {
    cls.__name__.lower(): (cls, base) for cls, base in [(Diphthong, Vowel), (Cluster, Consonant)]}


class TranscriptionSystem(TranscriptionBase):
    """
    A transcription System."""
    __type__ = 'ts'

    def __init__(self, path, metadata, features):
        """
        :param system: The name of a transcription system or a directory containing one.
        """
        super().__init__(path, None)
        if not (self.path.exists() and self.path.is_dir()):
            raise ValueError(f'unknown system: {self.path}')

        self.system = TableGroup.from_file(metadata)
        self.system._fname = path / 'metadata.json'

        self.features_to_sound: SoundsByFeatures = {}
        # dictionary for feature values, checks when writing elements from
        # write_order to make sure no output is doubled
        self._feature_values = {}

        self.diacritics_grapheme_by_value: BaseSoundclassMappingType = \
            {sc: {} for sc in get_args(BaseSoundclassType)}
        self.diacritics_value_by_grapheme: BaseSoundclassMappingType = \
            {sc: {} for sc in get_args(BaseSoundclassType)}

        for dia in itertable(self.system.tabledict['diacritics.tsv']):
            if not dia['alias'] and not dia['typography']:
                self.diacritics_grapheme_by_value[dia['type']][dia['value']] = dia['grapheme']
            # assign feature values to the dictionary
            self._feature_values[dia['value']] = dia['feature']
            self.diacritics_value_by_grapheme[dia['type']][dia['grapheme']] = dia['value']

        self.sound_classes: dict[BaseSoundclassOrMarkerType, type] = {}
        # the basic column structure, to allow for rendering
        self.columns: dict[BaseSoundclassOrMarkerType, list[str]] = {}
        self.sounds: dict[str, Sound] = {}  # Sounds by grapheme
        # check for unresolved aliased sounds
        aliases: list[tuple[str, frozenset[str]]] = []
        for cls in [Consonant, Vowel, Tone, Marker]:  # noqa: F405
            type_: BaseSoundclassOrMarkerType = cls.__name__.lower()
            self.sound_classes[type_] = cls
            # store information on column structure to allow for rendering of a sound in this form,
            # which will make it easier to insert it when finding generated sounds
            self.columns[type_] = [
                c['name'].lower() for c in
                self.system.tabledict[f'{type_}s.tsv'].asdict()['tableSchema']['columns']]

            for lnum, item in enumerate(itertable(self.system.tabledict[f'{type_}s.tsv'])):
                floc = f'{type_}s.tsv:{lnum + 2}:'
                if item['grapheme'] in self.sounds:
                    raise ValueError(f'{floc} duplicate grapheme: {item["grapheme"]}')

                try:
                    sound = cls.from_kw(ts=self, **item)
                except ValueError as e:
                    raise ValueError(f"{floc} {e}") from e

                for key in fieldnames(sound.__annotations__['features']):
                    value = getattr(sound.features, key)
                    if value and value not in self._feature_values:
                        self._feature_values[value] = key

                self.sounds[item['grapheme']] = sound
                if not sound.alias:
                    if sound.featureset in self.features_to_sound:  # pragma: no cover
                        raise ValueError(f'{floc} duplicate features: {sound.name}')
                    self.features_to_sound[sound.featureset] = sound
                else:
                    aliases.append((floc, sound.featureset))
        # Check for consistency of aliases: if an alias has no counterpart, it is orphaned and
        # needs to be deleted or given an accepted non-aliased sound.
        orphans = [floc for floc, featureset in aliases if featureset not in self.features_to_sound]
        if orphans:  # pragma: no cover
            raise ValueError(f'{" ".join(orphans)} orphaned aliases')

        # basic regular expression, used to match the basic sounds in the system, matching longest
        # first, then alphabetically.
        self._regex = re.compile('|'.join(
            map(re.escape, sorted(self.sounds, key=lambda x: (len(x), -ord(x[0])), reverse=True))))

        # normalization data
        self._normalize: dict[str, str] = {
            norm(r['source']): norm(r['target'])
            for r in itertable(self.system.tabledict['normalize.tsv'])}

    def _norm(self, string: str) -> str:
        """Extended normalization: normalize by list of norm-characters, split by character "/"."""
        nstring = norm(string)
        if "/" in string:
            s, t = string.split('/')
            nstring = t
        return self.normalize(nstring)

    def normalize(self, string):
        """Normalize the string according to normalization list"""
        return ''.join([self._normalize.get(x, x) for x in nfd(string)])

    def _from_name(self, string: str) -> Sound:
        """Parse a sound from its name"""
        components = string.split(' ')
        if frozenset(components) in self.features_to_sound:
            return self.features_to_sound[frozenset(components)]

        rest, sound_class = components[:-1], components[-1]
        if sound_class in COMPLEX_SOUNDS:
            m = re.fullmatch('from (?P<from>.*?) to (?P<to>.*?)', ' '.join(rest))
            if m:
                base_sound_class = COMPLEX_SOUNDS[sound_class][1].__name__.lower()
                from_, to_ = m.group('from'), m.group('to')
                s1 = self.features_to_sound.get(frozenset(from_.split(' ') + [base_sound_class]))
                s2 = self.features_to_sound.get(frozenset(to_.split(' ') + [base_sound_class]))

                if s1 and s2:
                    if sound_class == 'diphthong':
                        return Diphthong.from_sounds(s1 + s2, s1, s2, self)  # noqa: F405
                    return Cluster.from_sounds(s1 + s2, s1, s2, self)  # noqa: F405

                # try to generate the sounds if they are not there
                s1 = self._from_name(from_ + ' ' + base_sound_class)
                s2 = self._from_name(to_ + ' ' + base_sound_class)
                if not (isinstance(s1, UnknownSound) or isinstance(s2, UnknownSound)):
                    if sound_class == 'diphthong':
                        return Diphthong.from_sounds(s1 + s2, s1, s2, self)
                    return Cluster.from_sounds(s1 + s2, s1, s2, self)  # noqa: F405
                raise ValueError('components could not be found in system')  # pragma: no cover
            raise ValueError('name string is erroneously encoded')

        if sound_class in self.sound_classes:
            args = {self._feature_values.get(comp, '?'): comp for comp in rest}
            if '?' in args:
                raise ValueError('string contains unknown features')
            args['grapheme'] = ''
            args['ts'] = self
            sound = self.sound_classes[sound_class].from_kw(**args)
            if sound.featureset not in self.features_to_sound:
                sound.generated = True
                return sound
            return self.features_to_sound[sound.featureset]  # pragma: no cover

        raise ValueError('no sound class specified')

    def _from_symbol(self, string) -> Union[Sound, UnknownSound]:
        """Parse a string and return its features.

        :param string: A one-symbol string in NFD

        Notes
        -----
        Strategy is rather simple: we determine the base part of a string and
        then search left and right of this part for the additional features as
        expressed by the diacritics. Fails if a segment has more than one basic
        part.
        """
        nstring = self._norm(string)

        # check whether sound is in self.sounds
        if nstring in self.sounds:
            sound = self.sounds[nstring]
            sound.normalized = nstring != string
            sound.source = string
            return sound

        match = list(self._regex.finditer(nstring))

        if len(match) not in (1, 2):  # No match or more than two; both is considered an error.
            return UnknownSound(grapheme=nstring, source=string, ts=self)  # noqa: F405

        # if the match has length 2, we assume that we have two sounds, so we split the sound and
        # pass it on for separate evaluation (recursive function) we add a check that makes sure
        # there is no single-match if we take the second element
        checked_for_two, pre, mid, post = False, None, None, None
        if len(match) == 2:
            sound1 = self._from_symbol(nstring[:match[1].start()])
            sound2 = self._from_symbol(nstring[match[1].start():])
            # if we have ANY unknown sound, we mark the whole sound as unknown, if
            # we have two known sounds of the same type (vowel or consonant), we
            # either construct a diphthong or a cluster
            if sound1.type == sound2.type and sound1.type in ['consonant', 'vowel']:
                if Diphthong.match(sound1, sound2):
                    return Diphthong.from_sounds(string, sound1, sound2, self)

                if Cluster.match(sound1, sound2):
                    return Cluster.from_sounds(string, sound1, sound2, self)

                # check for plosive plus fricative if they are the same in manner
                if all((sound1.place == sound2.place,
                        sound1.manner == sound1.validated('manner', 'stop'),
                        sound2.manner == sound2.validated('manner', 'fricative'))):
                    # join features
                    features = {k: v for k, v in sound1.featuredict.items() if v}
                    for k, v in sound2.featuredict.items():
                        if v:
                            features.setdefault(k, v)
                    features['manner'] = sound1.validated('manner', 'affricate')
                    return self._from_name(' '.join(features.values()) + ' consonant')
            # So, two matches, but no Diphthong or Cluster.
            i = 1
            while i < len(nstring):  # We try matching with prefixes/diacritics chopped off ...
                new_match = list(self._regex.finditer(nstring[i:]))
                if len(new_match) == 1:
                    pre, mid, post = nstring[i:].partition(
                        nstring[i:][new_match[0].start():new_match[0].end()])
                    pre = nstring[:i] + pre
                    checked_for_two = True
                    break
                i += 1
            if not checked_for_two:  # pragma: no cover
                return UnknownSound(grapheme=nstring, source=string, ts=self)  # noqa: F405

        if not checked_for_two:
            pre, mid, post = nstring.partition(nstring[match[0].start():match[0].end()])
        return self._sound_with_custom_diacritics(string, nstring, pre, mid, post)

    def _sound_with_custom_diacritics(self, string, nstring, pre, mid, post):
        base_sound = self.sounds[mid]
        if isinstance(base_sound, Marker):  # noqa: F405
            assert pre or post
            return UnknownSound(grapheme=nstring, source=string, ts=self)  # noqa: F405

        # A base sound with diacritics or a custom symbol.
        features = base_sound.asdict()
        features.update(
            source=string,
            generated=True,
            normalized=nstring != string,
            base=base_sound.grapheme)

        # We construct two versions: the "normal" version and the version where we search for
        # aliases and normalize them (as our features system for diacritics may well define
        # aliases).
        grapheme, sound = '', ''
        for dia in [p + EMPTY for p in pre]:
            feature = self.diacritics_value_by_grapheme[base_sound.type].get(dia, {})
            if not feature:
                return UnknownSound(grapheme=nstring, source=string, ts=self)
            features[self._feature_values[feature]] = feature
            # we add the unaliased version to the grapheme
            grapheme += dia[0]
            # we add the corrected version (if this is needed) to the sound
            sound += self.diacritics_grapheme_by_value[base_sound.type][feature][0]
        # add the base sound
        grapheme += base_sound.grapheme
        sound += base_sound.s
        for dia in [EMPTY + p for p in post]:
            feature = self.diacritics_value_by_grapheme[base_sound.type].get(dia, {})
            # we are strict: if we don't know the feature, it's an unknown sound
            if not feature:
                return UnknownSound(grapheme=nstring, source=string, ts=self)
            features[self._feature_values[feature]] = feature
            grapheme += dia[1]
            sound += self.diacritics_grapheme_by_value[base_sound.type][feature][1]

        features['grapheme'] = sound
        new_sound = self.sound_classes[base_sound.type].from_kw(**features)
        # check whether grapheme differs from re-generated sound
        if str(new_sound) != sound:
            new_sound.alias = True
        if grapheme != sound:
            new_sound.alias = True
            new_sound.grapheme = grapheme
        return new_sound

    def resolve_sound(self, string):
        if isinstance(string, Sound):  # noqa: F405
            return self.features_to_sound[string.featureset]
        if isinstance(string, Symbol):  # noqa: F405
            return string
        if set(string.split(' ')).intersection(
                list(self.sound_classes) + ['diphthong', 'cluster']):
            return self._from_name(string)
        string = nfd(string)
        return self._from_symbol(string)

    @property
    def feature_system(self):
        return self._feature_values

    def __contains__(self, item):
        if isinstance(item, Sound):  # noqa: F405
            return item.featureset in self.features_to_sound
        return item in self.sounds

    def __iter__(self):
        return iter(self.sounds)
