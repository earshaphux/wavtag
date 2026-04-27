"""Tag normalization utilities for wavtag."""

import re
from typing import Optional
from wavtag.metadata import AudioMetadata


DEFAULT_RULES = {
    "title_case_fields": ["title", "artist", "album", "album_artist"],
    "strip_whitespace": True,
    "normalize_track_number": True,
    "remove_featuring": False,
}


def title_case(value: str) -> str:
    """Apply title case while preserving common lowercase words."""
    lowercase_words = {"a", "an", "the", "and", "but", "or", "for", "nor",
                       "on", "at", "to", "by", "in", "of", "up"}
    words = value.split()
    result = []
    for i, word in enumerate(words):
        if i == 0 or word.lower() not in lowercase_words:
            result.append(word.capitalize())
        else:
            result.append(word.lower())
    return " ".join(result)


def normalize_track_number(value: str) -> str:
    """Normalize track number to plain integer string (e.g. '03/12' -> '3')."""
    match = re.match(r"^(\d+)", value.strip())
    if match:
        return str(int(match.group(1)))
    return value


def strip_featuring(value: str) -> str:
    """Remove featuring credits from artist/title strings."""
    patterns = [
        r"\s*\(feat\.?.*?\)",
        r"\s*\[feat\.?.*?\]",
        r"\s*feat\.?\s+.*$",
    ]
    for pattern in patterns:
        value = re.sub(pattern, "", value, flags=re.IGNORECASE)
    return value.strip()


def normalize_metadata(metadata: AudioMetadata, rules: Optional[dict] = None) -> AudioMetadata:
    """Return a new AudioMetadata instance with normalized fields."""
    if rules is None:
        rules = DEFAULT_RULES

    fields = metadata.__dict__.copy()

    for field, value in fields.items():
        if value is None:
            continue

        if rules.get("strip_whitespace"):
            value = value.strip()

        if rules.get("remove_featuring") and field in ("title", "artist"):
            value = strip_featuring(value)

        if field in rules.get("title_case_fields", []):
            value = title_case(value)

        if rules.get("normalize_track_number") and field == "track_number" and value:
            value = normalize_track_number(value)

        fields[field] = value

    return AudioMetadata(**fields)
