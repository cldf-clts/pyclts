"""
CLTS groups transcription information into three categories:
Transcription systems (`ts`), transcription data (`td`) and soundclass systems (`sc`).
"""
import re
from typing import Literal, get_args, Union

from csvw import TableGroup

from pyclts.models import (
    Sound, UnknownSound, Cluster, Diphthong, Vowel, Consonant, Tone, Marker, Symbol,
    COMPLEX_SOUNDS, BaseSoundclassOrMarkerType, fieldnames)
from pyclts.util import read_data, SoundsType, NamesType, GraphemeMapType, DataType, nfd, norm, itertable
from .datatypes_util import TranscriptionBase, Diacritics, SymbolWithDiacritics

SoundsByFeatures = dict[frozenset, Sound]
FeatureValueType = str
FeatureNameType = str

DatatypeNameType = Literal['sc', 'td', 'ts']
SoundclassNameType = Literal['sca', 'cv', 'art', 'dolgo', 'asjp', 'color']
SOUNDCLASS_SYSTEMS = list(get_args(SoundclassNameType))


class SoundClasses(TranscriptionBase):
    """
    Class for handling sound class models.
    """
    def __init__(self, path, system, id_: SoundclassNameType):
        assert id_ in SOUNDCLASS_SYSTEMS
        super().__init__(path, system)
        self._id: SoundclassNameType = id_
        self.sounds: SoundsType
        self.names: NamesType
        _, data, self.sounds, self.names = read_data(self.path, self._id)
        self.data: dict[str, dict[str, str]] = {}
        self.classes: set[str] = set()
        for k, v in data.items():
            self.data[k] = v[0]
            self.classes.add(v[0]['grapheme'])

    @property
    def id(self) -> SoundclassNameType:
        """System identifier."""
        return self._id

    def resolve_sound(self, sound):
        """Function tries to identify a sound in the data.

        Notes
        -----
        The function tries to resolve sounds to take a sound with less complex
        features in order to yield the next approximate sound class, if the
        transcription data are sound classes.
        """
        sound = sound if isinstance(sound, Symbol) else self.system[sound]
        if sound.name in self.data:
            return self.data[sound.name]['grapheme']
        if not isinstance(sound, UnknownSound):
            if sound.type() in COMPLEX_SOUNDS:
                return self.resolve_sound(sound.from_sound)
            name = [
                s for s in sound.name.split(' ') if
                s not in sound.features.feature_values_excluded_in_str()]
            while len(name) >= 4:
                sound = self.system.get(' '.join(name))
                if sound and sound.name in self.data:
                    return self.resolve_sound(sound)
                name.pop(0)
        raise KeyError(":sc:resolve_sound: No sound could be found.")


class TranscriptionData(TranscriptionBase):
    """
    Class for handling transcription data.
    """
    def __init__(self, path, system):
        super().__init__(path, system)
        self.grapheme_map: GraphemeMapType
        self.data: DataType
        self.sounds: SoundsType
        self.names: NamesType
        self.grapheme_map, self.data, self.sounds, self.names = read_data(
            self.path,
            'GRAPHEME',
            'URL',
            'BIPA_GRAPHEME',
            'GENERATED',
            'URL',
            'LATEX',
            'FEATURES',
            'SOUND',
            'IMAGE',
            'COUNT',
            'NOTE',
            'EXPLICIT'
        )

    def resolve_sound(self, sound: Union[str, Sound]) -> str:
        """Function tries to identify a sound in the data.

        Notes
        -----
        The function tries to resolve sounds to take a sound with less complex
        features in order to yield the next approximate sound class, if the
        transcription data are sound classes.
        """
        if not isinstance(sound, Sound):
            sound = self.system[sound]
        if sound.name in self.data:
            return '//'.join([x['grapheme'] for x in self.data[sound.name]])
        raise KeyError(":td:resolve_sound: No sound could be found.")

    def resolve_grapheme(self, grapheme: str) -> Union[Sound, Symbol]:
        """Resolve a grapheme to a sound."""
        return self.system[self.grapheme_map[grapheme]]


class TranscriptionSystem(TranscriptionBase):  # pylint: disable=R0902
    """A transcription System."""
    def __init__(self, path, metadata):
        """
        :param system: The name of a transcription system or a directory containing one.
        """
        super().__init__(path, None)
        if not (self.path.exists() and self.path.is_dir()):
            raise ValueError(f'unknown system: {self.path}')

        self.system: TableGroup = TableGroup.from_file(metadata)
        self.system._fname = path / 'metadata.json'

        self.features_to_sound: SoundsByFeatures = {}
        # dictionary for feature values, checks when writing elements from
        # write_order to make sure no output is doubled
        self._feature_values: dict[FeatureValueType, FeatureNameType] = {}

        self.diacritics = Diacritics.from_table(
            self.system.tabledict['diacritics.tsv'], self._feature_values)

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
                if item['grapheme'] in self.sounds:  # pragma: no cover
                    raise ValueError(f'{floc} duplicate grapheme: {item["grapheme"]}')

                try:
                    sound = cls.from_kw(ts=self, **item)
                except ValueError as e:  # pragma: no cover
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

    def _norm(self, string: str, sep='/') -> str:
        """Extended normalization: normalize by list of norm-characters, split by character "/"."""
        nstring = norm(string)
        if sep in string:
            nstring = string.partition(sep)[2]
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
                    return COMPLEX_SOUNDS[sound_class][0].from_sounds(s1 + s2, s1, s2, self)

                # try to generate the sounds if they are not there
                s1 = self._from_name(from_ + ' ' + base_sound_class)
                s2 = self._from_name(to_ + ' ' + base_sound_class)
                if not (isinstance(s1, UnknownSound) or isinstance(s2, UnknownSound)):
                    return COMPLEX_SOUNDS[sound_class][0].from_sounds(s1 + s2, s1, s2, self)
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

        # If the match has length 2, we assume that we have two sounds, so we split the sound and
        # pass it on for separate evaluation (recursive function). Failing that, we try to interpret
        # the string as one sound decorated with left- and right-attaching diacritics.
        with_diacritics = None
        if len(match) == 2:
            sound1 = self._from_symbol(nstring[:match[1].start()])
            sound2 = self._from_symbol(nstring[match[1].start():])
            # if we have ANY unknown sound, we mark the whole sound as unknown, if
            # we have two known sounds of the same type (vowel or consonant), we
            # either construct a diphthong or a cluster
            if sound1.type() == sound2.type() and isinstance(sound1, (Consonant, Vowel)):
                for cls in [Diphthong, Cluster]:
                    if cls.match(sound1, sound2):
                        return cls.from_sounds(string, sound1, sound2, self)

                # check for plosive plus fricative if they are the same in manner
                if all((
                        sound1.features.place == sound2.features.place,
                        sound1.features.manner == sound1.features.validated('manner', 'stop'),
                        sound2.features.manner == sound2.features.validated('manner', 'fricative')
                )):
                    return self._affricate_consonant(sound1, sound2)
            # So, two matches, but no Diphthong or Cluster.
            i = 1
            while i < len(nstring):  # We try matching with prefixes/diacritics chopped off ...
                new_match = list(self._regex.finditer(nstring[i:]))
                if len(new_match) == 1:
                    with_diacritics = SymbolWithDiacritics(
                        *nstring[i:].partition(
                            nstring[i:][new_match[0].start():new_match[0].end()]))
                    with_diacritics.pre = nstring[:i] + with_diacritics.pre
                    break
                i += 1
            if not with_diacritics:  # pragma: no cover
                return UnknownSound(grapheme=nstring, source=string, ts=self)  # noqa: F405

        if not with_diacritics:
            with_diacritics = SymbolWithDiacritics(
                *nstring.partition(nstring[match[0].start():match[0].end()]))
        return self._sound_with_custom_diacritics(string, nstring, with_diacritics)

    def _affricate_consonant(self, sound1: Sound, sound2: Sound):
        # join features
        features = {k: v for k, v in sound1.featuredict.items() if v}
        for k, v in sound2.featuredict.items():
            if v:
                features.setdefault(k, v)
        features['manner'] = sound1.features.validated('manner', 'affricate')
        return self._from_name(' '.join(features.values()) + ' consonant')

    def _sound_with_custom_diacritics(self, string, nstring, comps):
        base_sound = self.sounds[comps.base]
        if isinstance(base_sound, Marker):  # noqa: F405
            assert comps.pre or comps.post
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
        grapheme, sound = [], []
        try:
            for feature in comps.iter_add_pre(self.diacritics, base_sound, grapheme, sound):
                features[self._feature_values[feature]] = feature
            grapheme.append(base_sound.grapheme)
            sound.append(base_sound.s)
            for feature in comps.iter_add_post(self.diacritics, base_sound, grapheme, sound):
                features[self._feature_values[feature]] = feature
        except ValueError:
            return UnknownSound(grapheme=nstring, source=string, ts=self)
        grapheme = ''.join(grapheme)
        sound = ''.join(sound)

        features['grapheme'] = sound
        new_sound = self.sound_classes[base_sound.type()].from_kw(**features)
        # check whether grapheme differs from re-generated sound
        if str(new_sound) != sound:
            new_sound.alias = True
        if grapheme != sound:
            new_sound.alias = True
            new_sound.grapheme = grapheme
        return new_sound

    def resolve_sound(self, sound) -> Union[Symbol, Sound]:
        if isinstance(sound, Sound):  # noqa: F405
            return self.features_to_sound[sound.featureset]
        if isinstance(sound, Symbol):  # noqa: F405
            return sound
        if set(sound.split(' ')).intersection(
                list(self.sound_classes) + ['diphthong', 'cluster']):
            return self._from_name(sound)
        sound = nfd(sound)
        return self._from_symbol(sound)

    def is_valid(self, sound: Symbol) -> bool:
        """Check the consistency of a given transcription system conversion"""
        if isinstance(sound, (Marker, UnknownSound)):
            return False
        s1 = self[sound.name]
        s2 = self[sound.s]
        return s1.name == s2.name and s1.s == s2.s

    @property
    def feature_system(self) -> dict[FeatureValueType, FeatureNameType]:
        """The feature values used in the system mapped to feature names."""
        return self._feature_values

    def __contains__(self, item):
        if isinstance(item, Sound):  # noqa: F405
            return item.featureset in self.features_to_sound
        return item in self.sounds

    def __iter__(self):
        return iter(self.sounds)
