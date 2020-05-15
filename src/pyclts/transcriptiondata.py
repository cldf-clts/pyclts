from pyclts.util import read_data, TranscriptionBase
from pyclts.transcriptionsystem import Sound


class TranscriptionData(TranscriptionBase):
    """
    Class for handling transcription data.
    """
    __type__ = 'td'

    def __init__(self, path, system):
        super().__init__(path, system)
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

    def resolve_sound(self, sound):
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

    def resolve_grapheme(self, grapheme):
        return self.system[self.grapheme_map[grapheme]]
