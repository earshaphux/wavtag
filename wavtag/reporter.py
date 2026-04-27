"""Generate summary reports of metadata across audio file collections."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from wavtag.metadata import AudioMetadata, read_metadata


@dataclass
class CollectionReport:
    total_files: int = 0
    missing_title: List[Path] = field(default_factory=list)
    missing_artist: List[Path] = field(default_factory=list)
    missing_album: List[Path] = field(default_factory=list)
    missing_track: List[Path] = field(default_factory=list)
    missing_year: List[Path] = field(default_factory=list)

    @property
    def complete_files(self) -> int:
        incomplete = set(
            self.missing_title
            + self.missing_artist
            + self.missing_album
            + self.missing_track
            + self.missing_year
        )
        return self.total_files - len(incomplete)

    def completeness_pct(self) -> float:
        if self.total_files == 0:
            return 0.0
        return round(self.complete_files / self.total_files * 100, 1)


def build_report(paths: List[Path]) -> CollectionReport:
    """Scan a list of audio file paths and build a CollectionReport."""
    report = CollectionReport(total_files=len(paths))

    for path in paths:
        try:
            meta = read_metadata(path)
        except Exception:
            # Count unreadable files as missing everything
            report.missing_title.append(path)
            report.missing_artist.append(path)
            report.missing_album.append(path)
            report.missing_track.append(path)
            report.missing_year.append(path)
            continue

        if not meta.title:
            report.missing_title.append(path)
        if not meta.artist:
            report.missing_artist.append(path)
        if not meta.album:
            report.missing_album.append(path)
        if not meta.track_number:
            report.missing_track.append(path)
        if not meta.year:
            report.missing_year.append(path)

    return report


def format_report(report: CollectionReport) -> str:
    """Return a human-readable string summary of a CollectionReport."""
    lines = [
        f"Files scanned : {report.total_files}",
        f"Complete files: {report.complete_files} ({report.completeness_pct()}%)",
        "",
        "Missing fields:",
        f"  title        : {len(report.missing_title)}",
        f"  artist       : {len(report.missing_artist)}",
        f"  album        : {len(report.missing_album)}",
        f"  track number : {len(report.missing_track)}",
        f"  year         : {len(report.missing_year)}",
    ]
    return "\n".join(lines)
