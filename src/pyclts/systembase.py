import pathlib

from .util import PathType
from .models import UnknownSound, Sound


class TranscriptionBase:
    """Functionality based on data read from files."""
    __type__ = None

    def __init__(self, path: PathType, system=None):
        self.path = pathlib.Path(path)
        self.system = system

    @property
    def id(self) -> str:
        """The directory/file name identifies the transcription."""
        return self.path.stem

    def resolve_sound(self, sound) -> Sound:
        """Abstract method"""
        raise NotImplementedError  # pragma: no cover

    def __getitem__(self, sound):
        """Return a Sound instance matching the specification."""
        return self.resolve_sound(sound)

    def get(self, sound, default=None):
        """Imitates dict.get, i.e. __getitem__ with default."""
        try:
            res = self[sound]
            if isinstance(res, UnknownSound) and default:
                return default
            return res
        except KeyError:
            return default

    def __call__(self, sounds, default="0") -> list:
        if isinstance(sounds, str):
            sounds = sounds.split()

        return [self.get(x, default=default) for x in sounds]

    def translate(self, string: str, target_system: dict[str, str]):
        """Translate symbols from one system to another."""
        return ' '.join(f"{target_system.get(self[s].name or '?', '?')}" for s in string.split())
