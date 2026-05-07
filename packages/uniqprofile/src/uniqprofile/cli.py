"""Command line interface for uniqprofile."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Optional

from uniqprofile import profile_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="uniqprofile",
        description="Profile local CSV, TSV, and JSONL files for UniqTools workflows.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    file_parser = subparsers.add_parser("file", help="Profile one local file.")
    file_parser.add_argument("path", help="Input file path.")
    file_parser.add_argument(
        "--format",
        choices=["auto", "csv", "tsv", "jsonl"],
        default="auto",
        help="Input format. Defaults to auto detection by extension.",
    )
    file_parser.add_argument("--key", help="Optional key column or JSON field.")
    file_parser.add_argument(
        "--encoding",
        default="utf-8-sig",
        help="Input encoding. Defaults to utf-8-sig to tolerate UTF-8 BOM files.",
    )
    file_parser.add_argument(
        "--sample-size",
        type=int,
        help="Profile at most this many valid rows or records.",
    )
    file_parser.add_argument(
        "--duplicate-sample-size",
        type=int,
        default=20,
        help="Maximum number of duplicate keys to include in the profile.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = profile_file(
            Path(args.path),
            format=args.format,
            key=args.key,
            encoding=args.encoding,
            sample_size=args.sample_size,
            duplicate_sample_size=args.duplicate_sample_size,
        )
    except (OSError, ValueError) as exc:
        print(f"uniqprofile: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
