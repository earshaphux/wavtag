"""CLI entry point for wavtag."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from wavtag.metadata import read_metadata, write_metadata
from wavtag.normalizer import normalize_metadata
from wavtag.reporter import build_report, format_report

AUDIO_EXTENSIONS = {".mp3", ".flac", ".wav", ".aiff", ".m4a", ".ogg"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wavtag",
        description="Batch edit and normalize audio file metadata.",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # normalize
    norm = sub.add_parser("normalize", help="Normalize metadata fields in audio files.")
    norm.add_argument("paths", nargs="+", type=Path, help="Files or directories to process.")
    norm.add_argument("--dry-run", action="store_true", help="Preview changes without writing.")

    # show
    show = sub.add_parser("show", help="Display metadata for audio files.")
    show.add_argument("paths", nargs="+", type=Path)

    # report
    rep = sub.add_parser("report", help="Print a completeness report for a collection.")
    rep.add_argument("paths", nargs="+", type=Path, help="Files or directories to scan.")

    return parser


def collect_files(paths: List[Path]) -> List[Path]:
    files: List[Path] = []
    for p in paths:
        if p.is_dir():
            files.extend(f for f in sorted(p.rglob("*")) if f.suffix.lower() in AUDIO_EXTENSIONS)
        elif p.suffix.lower() in AUDIO_EXTENSIONS:
            files.append(p)
    return files


def cmd_normalize(args: argparse.Namespace) -> None:
    files = collect_files(args.paths)
    if not files:
        print("No audio files found.", file=sys.stderr)
        return
    for path in files:
        meta = read_metadata(path)
        updated = normalize_metadata(meta)
        if args.dry_run:
            print(f"[dry-run] {path}: {updated}")
        else:
            write_metadata(path, updated)
            print(f"Normalized: {path}")


def cmd_show(args: argparse.Namespace) -> None:
    files = collect_files(args.paths)
    for path in files:
        meta = read_metadata(path)
        print(f"\n{path}")
        for key, value in meta.to_dict().items():
            print(f"  {key:<14}: {value or '—'}")


def cmd_report(args: argparse.Namespace) -> None:
    files = collect_files(args.paths)
    if not files:
        print("No audio files found.", file=sys.stderr)
        return
    report = build_report(files)
    print(format_report(report))


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "normalize":
        cmd_normalize(args)
    elif args.command == "show":
        cmd_show(args)
    elif args.command == "report":
        cmd_report(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
