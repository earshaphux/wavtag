"""Tests for wavtag.normalizer module."""

import pytest
from wavtag.metadata import AudioMetadata
from wavtag.normalizer import (
    title_case,
    normalize_track_number,
    strip_featuring,
    normalize_metadata,
    DEFAULT_RULES,
)


def make_metadata(**kwargs) -> AudioMetadata:
    defaults = dict(
        title=None, artist=None, album=None, album_artist=None,
        track_number=None, year=None, genre=None, comment=None,
    )
    defaults.update(kwargs)
    return AudioMetadata(**defaults)


def test_title_case_basic():
    assert title_case("hello world") == "Hello World"


def test_title_case_preserves_lowercase_words():
    result = title_case("the lord of the rings")
    assert result == "The Lord of the Rings"


def test_title_case_first_word_always_capitalized():
    assert title_case("a day in the life") == "A Day in the Life"


def test_normalize_track_number_plain():
    assert normalize_track_number("3") == "3"


def test_normalize_track_number_with_total():
    assert normalize_track_number("03/12") == "3"


def test_normalize_track_number_padded():
    assert normalize_track_number("07") == "7"


def test_strip_featuring_parens():
    assert strip_featuring("Song (feat. Someone)") == "Song"


def test_strip_featuring_brackets():
    assert strip_featuring("Song [feat. Someone]") == "Song"


def test_strip_featuring_inline():
    assert strip_featuring("Artist feat. Other") == "Artist"


def test_normalize_metadata_title_case():
    meta = make_metadata(title="hello world", artist="john doe", album="some album")
    result = normalize_metadata(meta)
    assert result.title == "Hello World"
    assert result.artist == "John Doe"
    assert result.album == "Some Album"


def test_normalize_metadata_track_number():
    meta = make_metadata(track_number="05/14")
    result = normalize_metadata(meta)
    assert result.track_number == "5"


def test_normalize_metadata_strips_whitespace():
    meta = make_metadata(title="  Spaces  ", artist=" Artist ")
    result = normalize_metadata(meta)
    assert result.title == "Spaces"
    assert result.artist == "Artist"


def test_normalize_metadata_none_fields_unchanged():
    meta = make_metadata(title=None, artist="artist")
    result = normalize_metadata(meta)
    assert result.title is None


def test_normalize_metadata_remove_featuring_off_by_default():
    meta = make_metadata(artist="Artist feat. Other")
    result = normalize_metadata(meta)
    assert "feat" in result.artist.lower()


def test_normalize_metadata_remove_featuring_enabled():
    rules = {**DEFAULT_RULES, "remove_featuring": True}
    meta = make_metadata(artist="Artist feat. Other")
    result = normalize_metadata(meta, rules=rules)
    assert "feat" not in result.artist.lower()
