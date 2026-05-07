"""Command line interface for uniqcheck."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from uniqdiff import UniqDiffError

from uniqcheck import (
    CompareCheckResult,
    FileCheckResult,
    SchemaCheckResult,
    check_csv_file,
    compare_csv_by_key,
    compare_csv_schema,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="uniqcheck",
        description="Run CI-friendly CSV checks backed by uniqdiff.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    file_parser = subparsers.add_parser("file", help="Check one CSV file.")
    file_parser.add_argument("path", help="CSV file path.")
    file_parser.add_argument("--key", help="Key column used for duplicate detection.")
    file_parser.add_argument(
        "--encoding",
        default="utf-8-sig",
        help="CSV encoding. Defaults to utf-8-sig to tolerate UTF-8 BOM files.",
    )
    file_parser.add_argument(
        "--required-column",
        action="append",
        default=[],
        metavar="COLUMN",
        help="Required CSV column. Can be repeated.",
    )
    file_parser.add_argument(
        "--fail-on-duplicates",
        action="store_true",
        help="Exit with code 1 when duplicate keys are found.",
    )
    file_parser.add_argument(
        "--fail-on-missing-columns",
        action="store_true",
        help="Exit with code 1 when required columns are missing.",
    )

    compare_parser = subparsers.add_parser("compare", help="Compare two CSV files by key.")
    compare_parser.add_argument("first", help="First CSV file.")
    compare_parser.add_argument("second", help="Second CSV file.")
    compare_parser.add_argument("--key", required=True, help="Key column used for comparison.")
    compare_parser.add_argument(
        "--encoding",
        default="utf-8-sig",
        help="CSV encoding. Defaults to utf-8-sig to tolerate UTF-8 BOM files.",
    )
    compare_parser.add_argument(
        "--mode",
        choices=["memory", "disk", "auto"],
        default="auto",
        help="uniqdiff execution mode.",
    )
    compare_parser.add_argument(
        "--fail-on-added",
        action="store_true",
        help="Exit with code 1 when rows are present only in the second file.",
    )
    compare_parser.add_argument(
        "--fail-on-removed",
        action="store_true",
        help="Exit with code 1 when rows are present only in the first file.",
    )
    compare_parser.add_argument(
        "--fail-on-duplicates",
        action="store_true",
        help="Exit with code 1 when duplicate keys are found in either file.",
    )

    schema_parser = subparsers.add_parser(
        "schema",
        help="Compare inferred CSV schemas with the uniqdiff 1.1 schema engine.",
    )
    schema_parser.add_argument("first", help="First CSV file.")
    schema_parser.add_argument("second", help="Second CSV file.")
    schema_parser.add_argument(
        "--encoding",
        default="utf-8-sig",
        help="CSV encoding. Defaults to utf-8-sig to tolerate UTF-8 BOM files.",
    )
    schema_parser.add_argument(
        "--sample-size",
        type=int,
        help="Infer schema from at most this many rows from each file.",
    )
    schema_parser.add_argument(
        "--empty-string-not-null",
        action="store_true",
        help="Treat empty strings as string values instead of nulls.",
    )
    schema_parser.add_argument(
        "--loose-numeric-types",
        action="store_true",
        help="Treat int and float values as a shared number type.",
    )
    schema_parser.add_argument(
        "--fail-on-schema-change",
        action="store_true",
        help="Exit with code 1 when schema differences are found.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "file":
            file_result = check_csv_file(
                Path(args.path),
                key=args.key,
                required_columns=tuple(args.required_column),
                encoding=args.encoding,
            )
            print(json.dumps(asdict(file_result), indent=2, sort_keys=True))
            return 1 if _file_should_fail(args, file_result) else 0

        if args.command == "compare":
            compare_result = compare_csv_by_key(
                Path(args.first),
                Path(args.second),
                key=args.key,
                mode=args.mode,
                encoding=args.encoding,
            )
            print(json.dumps(asdict(compare_result), indent=2, sort_keys=True))
            return 1 if _compare_should_fail(args, compare_result) else 0

        schema_result = compare_csv_schema(
            Path(args.first),
            Path(args.second),
            encoding=args.encoding,
            sample_size=args.sample_size,
            empty_string_null=not args.empty_string_not_null,
            strict_numeric_types=not args.loose_numeric_types,
        )
        print(json.dumps(asdict(schema_result), indent=2, sort_keys=True))
        return 1 if _schema_should_fail(args, schema_result) else 0
    except (OSError, ValueError, UniqDiffError) as exc:
        print(f"uniqcheck: {exc}", file=sys.stderr)
        return 2


def _file_should_fail(args: argparse.Namespace, result: FileCheckResult) -> bool:
    return bool(
        (args.fail_on_missing_columns and result.required_columns_missing)
        or (args.fail_on_duplicates and result.duplicate_key_count)
    )


def _compare_should_fail(args: argparse.Namespace, result: CompareCheckResult) -> bool:
    duplicates = result.duplicates_first + result.duplicates_second
    return bool(
        (args.fail_on_added and result.only_in_second)
        or (args.fail_on_removed and result.only_in_first)
        or (args.fail_on_duplicates and duplicates)
    )


def _schema_should_fail(args: argparse.Namespace, result: SchemaCheckResult) -> bool:
    return bool(args.fail_on_schema_change and result.has_changes)


if __name__ == "__main__":
    raise SystemExit(main())
