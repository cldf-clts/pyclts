"""
Transcription System module for consistent IPA handling.
========================================================

"""
import re

from csvw import TableGroup
from clldutils import jsonlib
import attr

from pyclts.util import nfd, norm, EMPTY, itertable, TranscriptionBase
from pyclts.models import *  # noqa: F403


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
            raise ValueError('unknown system: {0}'.format(self.path))

        self.system = TableGroup.from_file(metadata)
        self.system._fname = path / 'metadata.json'

        self.features = {'consonant': {}, 'vowel': {}, 'tone': {}}
        # dictionary for feature values, checks when writing elements from
        # write_order to make sure no output is doubled
        self._feature_values = {}

        # load the general features
        features = jsonlib.load(features)

        self.diacritics = dict(
            consonant={}, vowel={}, click={}, diphthong={}, tone={}, cluster={})
        for dia in itertable(self.system.tabledict['diacritics.tsv']):
            if not dia['alias'] and not dia['typography']:
                self.features[dia['type']][dia['value']] = dia['grapheme']
            # assign feature values to the dictionary
            self._feature_values[dia['value']] = dia['feature']
            self.diacritics[dia['type']][dia['grapheme']] = dia['value']

        self.sound_classes = {}
        self.columns = {}  # the basic column structure, to allow for rendering
        self.sounds = {}  # Sounds by grapheme
        self._covered = {}
        # check for unresolved aliased sounds
        aliases = []
        for cls in [Consonant, Vowel, Tone, Marker]:  # noqa: F405
            type_ = cls.__name__.lower()
            self.sound_classes[type_] = cls
            # store information on column structure to allow for rendering of a
            # sound in this form, which will make it easier to insert it when
            # finding generated sounds
            self.columns[type_] = [
                c['name'].lower() for c in
                self.system.tabledict['{0}s.tsv'.format(type_)]
                    .asdict()['tableSchema']['columns']]
            for lnum, item in enumerate(itertable(
                    self.system.tabledict['{0}s.tsv'.format(type_)])):
                if item['grapheme'] in self.sounds:
                    raise ValueError('duplicate grapheme in {0}:{1}: {2}'.format(
                        type_ + 's.tsv', lnum + 2, item['grapheme']))  # pragma: no cover
                sound = cls(ts=self, **item)
                # make sure this does not take too long
                for key, value in item.items():
                    if key not in {'grapheme', 'note', 'alias'} and \
                            value and value not in self._feature_values:
                        self._feature_values[value] = key
                        if type_ != 'marker' and value not in features[type_][key]:
                            raise ValueError(
                                "Unrecognized features ({0}: {1}, line {2}))".format(
                                    key, value, lnum + 2))  # pragma: no cover

                self.sounds[item['grapheme']] = sound
                if not sound.alias:
                    if sound.featureset in self.features:  # pragma: no cover
                        raise ValueError('duplicate features in {0}:{1}: {2}'.format(
                            type_ + 's.tsv', lnum + 2, sound.name))
                    self.features[sound.featureset] = sound
                else:
                    aliases += [(lnum, sound.type, sound.featureset)]
        # check for consistency of aliases: if an alias has no counterpart, it
        # is orphaned and needs to be deleted or given an accepted non-aliased
        # sound
        if [x for x in aliases if x[2] not in self.features]:  # pragma: no cover
            error = ', '.join(
                str(x[0] + 2) + '/' + str(x[1])
                for x in aliases if x[2] not in self.features)
            raise ValueError(
                'Orphaned aliases in line(s) {0}'.format(error))

        # basic regular expression, used to match the basic sounds in the system.
        self._regex = None
        self._update_regex()

        self._diacritic_regexes = None
        self._update_diacritic_regex()


        # normalization data
        self._normalize = {
            norm(r['source']): norm(r['target'])
            for r in itertable(self.system.tabledict['normalize.tsv'])}

    def _update_regex(self):
        self._regex = re.compile('|'.join(
            map(re.escape, sorted(self.sounds, key=lambda x: (len(x),
                -ord(x[0])), reverse=True))))

    def _update_diacritic_regex(self):
        """ Initializes the regexes for diacritics from the diacritic dictionnary.

        The structure of self.diacritic_regexes is:

        ```
            {type: (regex_pre, regex_post)}
        ```


        """
        self._diacritic_regexes = {}

        for d_type in self.diacritics:
            pre_diacritics = []
            post_diacritics = []

            for d in self.diacritics[d_type]:
                if d is not None: # Syllabic has None as a value: is this intended ?
                    if d[-1] == EMPTY:
                        pre_diacritics.append(d[:-1])
                    elif d[0] == EMPTY:
                        post_diacritics.append(d[1:])
                    else:
                        raise ValueError("Diacritics must contain {}".format(EMPTY))

            pre_regex = re.compile('(' + '|'.join(map(re.escape,
                sorted(pre_diacritics, key=lambda x: (len(x),
                -ord(x[0])), reverse=True))) +')')
            post_regex = re.compile('(' + '|'.join(map(re.escape,
                sorted(post_diacritics, key=lambda x: (len(x),
                -ord(x[0])), reverse=True))) + ')')

            self._diacritic_regexes[d_type] =  (pre_regex, post_regex)



    def _norm(self, string):
        """Extended normalization: normalize by list of norm-characters, split
        by character "/"."""
        nstring = norm(string)
        if "/" in string:
            s, t = string.split('/')
            nstring = t
        return self.normalize(nstring)

    def normalize(self, string):
        """Normalize the string according to normalization list"""
        return ''.join([self._normalize.get(x, x) for x in nfd(string)])

    def _from_name(self, string):
        """Parse a sound from its name"""
        components = string.split(' ')
        if frozenset(components) in self.features:
            return self.features[frozenset(components)]
        rest, sound_class = components[:-1], components[-1]
        if sound_class in ['diphthong', 'cluster']:
            if string.startswith('from ') and 'to ' in string:
                extension = {'diphthong': 'vowel', 'cluster': 'consonant'}[sound_class]
                string_ = ' '.join(string.split(' ')[1:-1])
                from_, to_ = string_.split(' to ')
                v1, v2 = frozenset(from_.split(' ') + [extension]), frozenset(
                    to_.split(' ') + [extension])
                if v1 in self.features and v2 in self.features:
                    s1, s2 = (self.features[v1], self.features[v2])
                    if sound_class == 'diphthong':
                        return Diphthong.from_sounds(s1 + s2, s1, s2, self)  # noqa: F405
                    else:
                        return Cluster.from_sounds(s1 + s2, s1, s2, self)  # noqa: F405
                else:
                    # try to generate the sounds if they are not there
                    s1, s2 = self._from_name(from_ + ' ' + extension), self._from_name(
                        to_ + ' ' + extension)
                    if not (
                            isinstance(s1, UnknownSound)  # noqa: F405
                            or isinstance(s2, UnknownSound)):  # noqa: F405
                        if sound_class == 'diphthong':
                            return Diphthong.from_sounds(  # noqa: F405
                                s1 + s2, s1, s2, self)
                        return Cluster.from_sounds(s1 + s2, s1, s2, self)  # noqa: F405
                    raise ValueError('components could not be found in system')  # pragma: no cover
            else:
                raise ValueError('name string is erroneously encoded')

        if sound_class not in self.sound_classes:
            raise ValueError('no sound class specified')

        args = {self._feature_values.get(comp, '?'): comp for comp in rest}
        if '?' in args:
            raise ValueError('string contains unknown features')
        args['grapheme'] = ''
        args['ts'] = self
        sound = self.sound_classes[sound_class](**args)
        if sound.featureset not in self.features:
            sound.generated = True
            return sound
        return self.features[sound.featureset]  # pragma: no cover

    def _parse(self, string):
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

        if len(match) != 1 and len(match) != 2:
            # Either no match or more than one; both is considered an error.
            return UnknownSound(grapheme=nstring, source=string, ts=self)  # noqa: F405

        # if the match has length 2, we assume that we have two sounds, so we split
        # the sound and pass it on for separate evaluation (recursive function)
        # we add a check that makes sure there is no single-match if we take
        # the second element
        checked_for_two = False
        if len(match) == 2:
            sound1 = self._parse(nstring[:match[1].start()])
            sound2 = self._parse(nstring[match[1].start():])
            # if we have ANY unknown sound, we mark the whole sound as unknown, if
            # we have two known sounds of the same type (vowel or consonant), we
            # either construct a diphthong or a cluster
            if 'unknownsound' not in (sound1.type, sound2.type) and \
                    sound1.type == sound2.type and sound1.type in ['consonant', 'vowel']:
                # diphthong creation
                if sound1.type == 'vowel':
                    return Diphthong.from_sounds(  # noqa: F405
                        string, sound1, sound2, self)
                elif sound1.type == 'consonant' and \
                        sound1.manner in ('stop', 'implosive', 'click', 'nasal') and \
                        sound2.manner in ('stop', 'implosive', 'affricate'):
                    return Cluster.from_sounds(  # noqa: F405
                        string, sound1, sound2, self)
                elif sound1.type == 'consonant' and sound1.manner == 'click' \
                        and sound2.manner == 'fricative':
                    return Cluster.from_sounds(string, sound1, sound2, self)  # noqa: F405
                # check for plosive plus fricative if they are the same in
                # manner
                elif sound1.manner == 'stop' and sound2.manner == 'fricative' \
                        and sound1.place == sound2.place:
                    # join features
                    features = {
                        f: v or sound2.featuredict[f] for f, v in sound1.featuredict.items()}
                    features['manner'] = 'affricate'
                    # new_sound = Consonant(self, nstring, **features)
                    new_sound = self._from_name(
                        ' '.join([v for k, v in features.items() if v]) + ' consonant')
                    return new_sound

            i = 1
            while i < len(nstring):
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
        base_sound = self.sounds[mid]
        if isinstance(base_sound, Marker):  # noqa: F405
            assert pre or post
            return UnknownSound(grapheme=nstring, source=string, ts=self)  # noqa: F405

        # A base sound with diacritics or a custom symbol.
        features = attr.asdict(base_sound)
        features.update(
            source=string,
            generated=True,
            normalized=nstring != string,
            base=base_sound.grapheme)

        # we construct two versions: the "normal" version and the version where
        # we search for aliases and normalize them (as our features system for
        # diacritics may well define aliases
        grapheme, sound = '', ''
        pre_dia_regex, post_dia_regex = self._diacritic_regexes[base_sound.type]

        for dia in pre_dia_regex.split(pre):
            # split with match group returns empty strings between matches
            # empty strings can be ignored
            if dia:
                feature = self.diacritics[base_sound.type].get(dia + EMPTY, {})
                if not feature:
                    return UnknownSound(  # noqa: F405
                        grapheme=nstring, source=string, ts=self)
                features[self._feature_values[feature]] = feature
                # we add the unaliased version to the grapheme
                grapheme += dia
                # we add the corrected version (if this is needed) to the sound
                sound += self.features[base_sound.type][feature][0]

        # add the base sound
        grapheme += base_sound.grapheme
        sound += base_sound.s
        for dia in post_dia_regex.split(post):
            # split with match group returns empty strings between matches
            # empty strings can be ignored
            if dia:
                feature = self.diacritics[base_sound.type].get(EMPTY + dia, {})
                # we are strict: if we don't know the feature, it's an unknown
                # sound
                if not feature:
                    return UnknownSound(  # noqa: F405
                        grapheme=nstring, source=string, ts=self)
                features[self._feature_values[feature]] = feature
                grapheme += dia
                sound += self.features[base_sound.type][feature][1]

        features['grapheme'] = sound
        new_sound = self.sound_classes[base_sound.type](**features)
        # check whether grapheme differs from re-generated sound
        if str(new_sound) != sound:
            new_sound.alias = True
        if grapheme != sound:
            new_sound.alias = True
            new_sound.grapheme = grapheme
        return new_sound

    def resolve_sound(self, string):
        if isinstance(string, Sound):  # noqa: F405
            return self.features[string.featureset]
        elif isinstance(string, Symbol):  # noqa: F405
            return string
        if set(string.split(' ')).intersection(
                list(self.sound_classes) + ['diphthong', 'cluster']):
            return self._from_name(string)
        string = nfd(string)
        return self._parse(string)

    @property
    def feature_system(self):
        return self._feature_values

    def __contains__(self, item):
        if isinstance(item, Sound):  # noqa: F405
            return item.featureset in self.features
        return item in self.sounds

    def __iter__(self):
        return iter(self.sounds)
