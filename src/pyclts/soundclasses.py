"""
Soundclass systems categorize sounds.
"""
from typing import Literal, get_args

from pyclts.models import UnknownSound, COMPLEX_SOUNDS, Symbol
from pyclts.util import read_data, SoundsType, NamesType
from .systembase import TranscriptionBase

SoundclassNameType = Literal['sca', 'cv', 'art', 'dolgo', 'asjp', 'color']
SOUNDCLASS_SYSTEMS = list(get_args(SoundclassNameType))


class SoundClasses(TranscriptionBase):
    """
    Class for handling sound class models.
    """
    __type__ = 'sc'

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
    def id(self) -> str:
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
