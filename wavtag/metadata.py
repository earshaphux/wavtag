"""Core metadata reading and writing for audio files."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3NoHeaderError
except ImportError:
    raise ImportError("mutagen is required: pip install mutagen")


@dataclass
class AudioMetadata:
    """Normalized representation of audio file tags."""

    path: Path
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    year: Optional[str] = None
    track: Optional[str] = None
    genre: Optional[str] = None
    comment: Optional[str] = None
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "year": self.year,
            "track": self.track,
            "genre": self.genre,
            "comment": self.comment,
        }


def read_metadata(path: Path) -> AudioMetadata:
    """Read metadata from an audio file and return an AudioMetadata instance."""
    audio = MutagenFile(path, easy=True)
    if audio is None:
        raise ValueError(f"Unsupported or unreadable file: {path}")

    def _get(key: str) -> Optional[str]:
        val = audio.tags.get(key) if audio.tags else None
        return val[0] if val else None

    return AudioMetadata(
        path=path,
        title=_get("title"),
        artist=_get("artist"),
        album=_get("album"),
        year=_get("date"),
        track=_get("tracknumber"),
        genre=_get("genre"),
        comment=_get("comment"),
    )


def write_metadata(meta: AudioMetadata) -> None:
    """Write an AudioMetadata instance back to the audio file."""
    audio = MutagenFile(meta.path, easy=True)
    if audio is None:
        raise ValueError(f"Unsupported or unreadable file: {meta.path}")

    if audio.tags is None:
        audio.add_tags()

    mapping = {
        "title": meta.title,
        "artist": meta.artist,
        "album": meta.album,
        "date": meta.year,
        "tracknumber": meta.track,
        "genre": meta.genre,
        "comment": meta.comment,
    }

    for key, value in mapping.items():
        if value is not None:
            audio.tags[key] = [value]
        elif key in audio.tags:
            del audio.tags[key]

    audio.save()
