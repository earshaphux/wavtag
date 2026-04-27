"""Tests for wavtag.reporter."""

from pathlib import Path
from unittest.mock import patch

import pytest

from wavtag.metadata import AudioMetadata
from wavtag.reporter import CollectionReport, build_report, format_report


def _meta(**kwargs) -> AudioMetadata:
    defaults = dict(title=None, artist=None, album=None, track_number=None, year=None, genre=None, comment=None)
    defaults.update(kwargs)
    return AudioMetadata(**defaults)


@pytest.fixture()
def three_paths():
    return [Path("a.mp3"), Path("b.mp3"), Path("c.mp3")]


def test_build_report_all_complete(three_paths):
    full = _meta(title="T", artist="A", album="AL", track_number="1", year="2020")
    with patch("wavtag.reporter.read_metadata", return_value=full):
        report = build_report(three_paths)
    assert report.total_files == 3
    assert report.complete_files == 3
    assert report.missing_title == []


def test_build_report_missing_fields(three_paths):
    metas = [
        _meta(title=None, artist="A", album="AL", track_number="1", year="2020"),
        _meta(title="T", artist=None, album="AL", track_number="1", year="2020"),
        _meta(title="T", artist="A", album="AL", track_number="1", year="2020"),
    ]
    with patch("wavtag.reporter.read_metadata", side_effect=metas):
        report = build_report(three_paths)

    assert len(report.missing_title) == 1
    assert len(report.missing_artist) == 1
    assert report.complete_files == 1


def test_build_report_unreadable_file():
    paths = [Path("bad.mp3")]
    with patch("wavtag.reporter.read_metadata", side_effect=Exception("oops")):
        report = build_report(paths)
    assert report.total_files == 1
    assert len(report.missing_title) == 1
    assert report.complete_files == 0


def test_completeness_pct_empty():
    report = CollectionReport(total_files=0)
    assert report.completeness_pct() == 0.0


def test_completeness_pct_partial():
    report = CollectionReport(
        total_files=4,
        missing_title=[Path("x.mp3"), Path("y.mp3")],
    )
    assert report.completeness_pct() == 50.0


def test_format_report_contains_key_info():
    report = CollectionReport(
        total_files=10,
        missing_title=[Path("a.mp3")],
        missing_artist=[Path("b.mp3"), Path("c.mp3")],
    )
    output = format_report(report)
    assert "10" in output
    assert "title" in output
    assert "artist" in output
    assert "%" in output


def test_format_report_completeness_line():
    full = _meta(title="T", artist="A", album="AL", track_number="1", year="2020")
    paths = [Path("a.mp3")]
    with patch("wavtag.reporter.read_metadata", return_value=full):
        report = build_report(paths)
    output = format_report(report)
    assert "100.0%" in output
