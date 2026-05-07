"""Lightweight local file profiling for UniqTools workflows."""

from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass(frozen=True)
class FileProfile:
    """Machine-readable profile for one local file."""

    path: str
    format: str
    size_bytes: int
    row_count: int
    sampled: bool = False
    columns: list[str] = field(default_factory=list)
    empty_counts: dict[str, int] = field(default_factory=dict)
    key: Optional[str] = None
    duplicate_key_count: int = 0
    duplicate_keys_sample: list[str] = field(default_factory=list)
    invalid_record_count: int = 0
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def has_warnings(self) -> bool:
        return bool(self.warnings or self.invalid_record_count)


def profile_file(
    path: Path,
    *,
    format: str = "auto",
    key: Optional[str] = None,
    encoding: str = "utf-8-sig",
    delimiter: Optional[str] = None,
    sample_size: Optional[int] = None,
    duplicate_sample_size: int = 20,
) -> FileProfile:
    """Profile one supported local file."""

    detected_format = _detect_format(path, format=format)
    if detected_format in {"csv", "tsv"}:
        return profile_delimited_file(
            path,
            format=detected_format,
            key=key,
            encoding=encoding,
            delimiter="\t" if detected_format == "tsv" else delimiter,
            sample_size=sample_size,
            duplicate_sample_size=duplicate_sample_size,
        )
    if detected_format == "jsonl":
        return profile_jsonl_file(
            path,
            key=key,
            encoding=encoding,
            sample_size=sample_size,
            duplicate_sample_size=duplicate_sample_size,
        )
    raise ValueError(f"Unsupported profile format: {detected_format!r}")


def profile_delimited_file(
    path: Path,
    *,
    format: str = "csv",
    key: Optional[str] = None,
    encoding: str = "utf-8-sig",
    delimiter: Optional[str] = None,
    sample_size: Optional[int] = None,
    duplicate_sample_size: int = 20,
) -> FileProfile:
    """Profile CSV or TSV rows with a header."""

    if sample_size is not None and sample_size < 0:
        raise ValueError("sample_size must be greater than or equal to zero")

    row_count = 0
    sampled = False
    empty_counts: Counter[str] = Counter()
    key_counter: Counter[str] = Counter()
    warnings: list[str] = []

    with path.open("r", encoding=encoding, newline="") as file:
        reader = csv.DictReader(file, delimiter=delimiter or ",")
        columns = list(reader.fieldnames or [])
        if key is not None and key not in columns:
            warnings.append(f"Key column {key!r} was not found.")

        for row in reader:
            if sample_size is not None and row_count >= sample_size:
                sampled = True
                break
            row_count += 1
            for column in columns:
                if row.get(column) in {None, ""}:
                    empty_counts[column] += 1
            if key is not None and key in row:
                key_counter[row[key]] += 1

    duplicate_keys = sorted(item for item, count in key_counter.items() if count > 1)
    return FileProfile(
        path=str(path),
        format=format,
        size_bytes=path.stat().st_size,
        row_count=row_count,
        sampled=sampled,
        columns=columns,
        empty_counts={column: empty_counts[column] for column in columns},
        key=key,
        duplicate_key_count=sum(key_counter[item] - 1 for item in duplicate_keys),
        duplicate_keys_sample=duplicate_keys[:duplicate_sample_size],
        warnings=warnings,
    )


def profile_jsonl_file(
    path: Path,
    *,
    key: Optional[str] = None,
    encoding: str = "utf-8-sig",
    sample_size: Optional[int] = None,
    duplicate_sample_size: int = 20,
) -> FileProfile:
    """Profile newline-delimited JSON objects."""

    if sample_size is not None and sample_size < 0:
        raise ValueError("sample_size must be greater than or equal to zero")

    row_count = 0
    sampled = False
    invalid_record_count = 0
    columns: set[str] = set()
    empty_counts: Counter[str] = Counter()
    key_counter: Counter[str] = Counter()
    warnings: list[str] = []

    with path.open("r", encoding=encoding) as file:
        for line in file:
            if sample_size is not None and row_count >= sample_size:
                sampled = True
                break
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError:
                invalid_record_count += 1
                continue
            if not isinstance(record, dict):
                invalid_record_count += 1
                continue
            row_count += 1
            columns.update(str(item) for item in record)
            for column, value in record.items():
                if value is None or value == "":
                    empty_counts[str(column)] += 1
            if key is not None:
                if key in record:
                    key_counter[str(record[key])] += 1
                else:
                    warnings.append(f"Key field {key!r} was missing in at least one record.")

    ordered_columns = sorted(columns)
    duplicate_keys = sorted(item for item, count in key_counter.items() if count > 1)
    return FileProfile(
        path=str(path),
        format="jsonl",
        size_bytes=path.stat().st_size,
        row_count=row_count,
        sampled=sampled,
        columns=ordered_columns,
        empty_counts={column: empty_counts[column] for column in ordered_columns},
        key=key,
        duplicate_key_count=sum(key_counter[item] - 1 for item in duplicate_keys),
        duplicate_keys_sample=duplicate_keys[:duplicate_sample_size],
        invalid_record_count=invalid_record_count,
        warnings=sorted(set(warnings)),
    )


def _detect_format(path: Path, *, format: str) -> str:
    if format != "auto":
        return format.lower()
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return "csv"
    if suffix == ".tsv":
        return "tsv"
    if suffix in {".jsonl", ".ndjson"}:
        return "jsonl"
    return "csv"
