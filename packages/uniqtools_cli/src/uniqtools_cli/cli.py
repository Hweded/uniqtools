"""Unified CLI entrypoint for UniqTools packages."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from typing import Optional

from uniqcheck.cli import main as check_main
from uniqprofile.cli import main as profile_main
from uniqrowdiff.cli import main as rowdiff_main

CommandMain = Callable[[Optional[Sequence[str]]], int]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="uniqtools",
        description="Unified entrypoint for UniqTools data workflow commands.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("profile", help="Profile local CSV, TSV, and JSONL files.")
    subparsers.add_parser("check", help="Run CI-friendly checks.")
    subparsers.add_parser("rowdiff", help="Compare changed fields for keyed CSV rows.")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        build_parser().print_help()
        return 2

    command = args[0]
    rest = args[1:]
    dispatch: dict[str, CommandMain] = {
        "profile": profile_main,
        "check": check_main,
        "rowdiff": rowdiff_main,
    }
    target = dispatch.get(command)
    if target is None:
        build_parser().parse_args(args)
        return 2
    return target(rest)


if __name__ == "__main__":
    raise SystemExit(main())
