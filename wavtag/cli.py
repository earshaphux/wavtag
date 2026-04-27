"""CLI entry point for wavtag."""

import argparse
import sys
from pathlib import Path

from wavtag.metadata import read_metadata, write_metadata
from wavtag.normalizer import normalize_metadata, DEFAULT_RULES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wavtag",
        description="Batch edit and normalize metadata tags across audio files.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # normalize subcommand
    norm = subparsers.add_parser("normalize", help="Normalize tags in audio files.")
    norm.add_argument("paths", nargs="+", help="Audio files or directories to process.")
    norm.add_argument("--dry-run", action="store_true", help="Preview changes without writing.")
    norm.add_argument("--remove-featuring", action="store_true",
                      help="Strip featuring credits from artist/title fields.")

    # show subcommand
    show = subparsers.add_parser("show", help="Display metadata for audio files.")
    show.add_argument("paths", nargs="+", help="Audio files or directories to inspect.")

    return parser


def collect_files(paths: list[str]) -> list[Path]:
    """Expand directories and return a flat list of audio file paths."""
    audio_extensions = {".mp3", ".flac", ".ogg", ".m4a", ".wav"}
    result = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            result.extend(f for f in p.rglob("*") if f.suffix.lower() in audio_extensions)
        elif p.is_file():
            result.append(p)
        else:
            print(f"Warning: {raw} not found, skipping.", file=sys.stderr)
    return sorted(result)


def cmd_normalize(args: argparse.Namespace) -> int:
    rules = {**DEFAULT_RULES, "remove_featuring": args.remove_featuring}
    files = collect_files(args.paths)
    if not files:
        print("No audio files found.")
        return 1

    for path in files:
        try:
            original = read_metadata(path)
            normalized = normalize_metadata(original, rules=rules)
            if args.dry_run:
                print(f"[dry-run] {path}: would normalize tags")
            else:
                write_metadata(path, normalized)
                print(f"Updated: {path}")
        except Exception as exc:  # noqa: BLE001
            print(f"Error processing {path}: {exc}", file=sys.stderr)
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    files = collect_files(args.paths)
    if not files:
        print("No audio files found.")
        return 1

    for path in files:
        try:
            meta = read_metadata(path)
            print(f"\n{path}")
            for key, value in meta.__dict__.items():
                print(f"  {key:<16} {value}")
        except Exception as exc:  # noqa: BLE001
            print(f"Error reading {path}: {exc}", file=sys.stderr)
    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    handlers = {"normalize": cmd_normalize, "show": cmd_show}
    sys.exit(handlers[args.command](args))


if __name__ == "__main__":
    main()
