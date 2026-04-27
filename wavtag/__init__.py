"""wavtag — batch audio metadata editor."""

__version__ = "0.1.0"
__author__ = "wavtag contributors"

from wavtag.metadata import AudioMetadata, read_metadata, write_metadata

__all__ = ["AudioMetadata", "read_metadata", "write_metadata"]
