"""Lightweight CSV checks backed by public uniqdiff APIs."""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from uniqdiff.engine import compare_file_schema, compare_files


@dataclass(frozen=True)
class FileCheckResult:
    """Result for checks against one CSV file."""

    path: str
    row_count: int
    required_columns_missing: list[str]
    duplicate_key_count: int
    duplicate_keys: list[str]

    @property
    def passed(self) -> bool:
        return not self.required_columns_missing and self.duplicate_key_count == 0


@dataclass(frozen=True)
class CompareCheckResult:
    """Result for checks comparing two CSV files by key."""

    first: str
    second: str
    only_in_first: int
    only_in_second: int
    common: int
    duplicates_first: int
    duplicates_second: int
    backend: Optional[str]


@dataclass(frozen=True)
class SchemaCheckResult:
    """Schema-aware comparison result backed by uniqdiff 1.1."""

    first: str
    second: str
    added_columns: list[str]
    removed_columns: list[str]
    type_changes: list[dict[str, Any]]
    nullable_changes: list[dict[str, Any]]
    sampled: bool
    warnings: list[str]

    @property
    def has_changes(self) -> bool:
        return bool(
            self.added_columns
            or self.removed_columns
            or self.type_changes
            or self.nullable_changes
        )


def check_csv_file(
    path: Path,
    *,
    key: Optional[str] = None,
    required_columns: tuple[str, ...] = (),
    encoding: str = "utf-8-sig",
) -> FileCheckResult:
    """Check required columns and duplicate keys in one CSV file."""

    row_count = 0
    key_counter: Counter[str] = Counter()
    with path.open("r", encoding=encoding, newline="") as file:
        reader = csv.DictReader(file)
        fieldnames = list(reader.fieldnames or [])
        missing = [column for column in required_columns if column not in fieldnames]
        if key is not None and key not in fieldnames:
            missing = [*missing, key]

        for row in reader:
            row_count += 1
            if key is not None and key in row:
                key_counter[row[key]] += 1

    duplicate_keys = sorted(key for key, count in key_counter.items() if count > 1)
    return FileCheckResult(
        path=str(path),
        row_count=row_count,
        required_columns_missing=missing,
        duplicate_key_count=sum(key_counter[key] - 1 for key in duplicate_keys),
        duplicate_keys=duplicate_keys,
    )


def compare_csv_by_key(
    first: Path,
    second: Path,
    *,
    key: str,
    mode: str = "auto",
    encoding: str = "utf-8-sig",
) -> CompareCheckResult:
    """Compare two CSV files by key through the public uniqdiff engine API."""

    result = compare_files(
        str(first),
        str(second),
        format="csv",
        encoding=encoding,
        key=key,
        mode=mode,
        include_common=True,
        include_duplicates=True,
    )
    return CompareCheckResult(
        first=str(first),
        second=str(second),
        only_in_first=result.stats.only_in_first_count,
        only_in_second=result.stats.only_in_second_count,
        common=result.stats.common_count,
        duplicates_first=result.stats.duplicate_first_count,
        duplicates_second=result.stats.duplicate_second_count,
        backend=result.metadata.get("backend"),
    )


def compare_csv_schema(
    first: Path,
    second: Path,
    *,
    encoding: str = "utf-8-sig",
    sample_size: Optional[int] = None,
    empty_string_null: bool = True,
    strict_numeric_types: bool = True,
) -> SchemaCheckResult:
    """Compare inferred CSV schemas through the public uniqdiff engine API."""

    result = compare_file_schema(
        str(first),
        str(second),
        format="csv",
        encoding=encoding,
        sample_size=sample_size,
        empty_string_null=empty_string_null,
        strict_numeric_types=strict_numeric_types,
    )
    return SchemaCheckResult(
        first=str(first),
        second=str(second),
        added_columns=result.added_columns,
        removed_columns=result.removed_columns,
        type_changes=result.type_changes,
        nullable_changes=result.nullable_changes,
        sampled=result.left_schema.sampled or result.right_schema.sampled,
        warnings=result.warnings,
    )
