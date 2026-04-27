"""Tests for wavtag.metadata read/write functionality."""

import shutil
from pathlib import Path

import pytest

from wavtag.metadata import AudioMetadata, read_metadata, write_metadata

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_mp3(tmp_path):
    """Copy the fixture MP3 to a temp dir so tests don't mutate the original."""
    src = FIXTURES_DIR / "sample.mp3"
    if not src.exists():
        pytest.skip("sample.mp3 fixture not found")
    dest = tmp_path / "sample.mp3"
    shutil.copy(src, dest)
    return dest


def test_read_metadata_returns_audio_metadata(sample_mp3):
    meta = read_metadata(sample_mp3)
    assert isinstance(meta, AudioMetadata)
    assert meta.path == sample_mp3


def test_read_metadata_fields_are_str_or_none(sample_mp3):
    meta = read_metadata(sample_mp3)
    for value in meta.to_dict().values():
        assert value is None or isinstance(value, str)


def test_write_and_read_roundtrip(sample_mp3):
    meta = read_metadata(sample_mp3)
    meta.title = "Test Title"
    meta.artist = "Test Artist"
    meta.album = "Test Album"
    meta.year = "2024"
    write_metadata(meta)

    updated = read_metadata(sample_mp3)
    assert updated.title == "Test Title"
    assert updated.artist == "Test Artist"
    assert updated.album == "Test Album"
    assert updated.year == "2024"


def test_write_clears_none_fields(sample_mp3):
    meta = read_metadata(sample_mp3)
    meta.title = "Will Be Removed"
    write_metadata(meta)

    meta2 = read_metadata(sample_mp3)
    meta2.title = None
    write_metadata(meta2)

    meta3 = read_metadata(sample_mp3)
    assert meta3.title is None


def test_unsupported_file_raises(tmp_path):
    bad_file = tmp_path / "not_audio.txt"
    bad_file.write_text("hello")
    with pytest.raises(ValueError, match="Unsupported"):
        read_metadata(bad_file)


def test_to_dict_keys(sample_mp3):
    meta = read_metadata(sample_mp3)
    d = meta.to_dict()
    expected_keys = {"title", "artist", "album", "year", "track", "genre", "comment"}
    assert set(d.keys()) == expected_keys
