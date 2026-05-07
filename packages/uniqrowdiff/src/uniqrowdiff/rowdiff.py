"""CSV row-level changed-field analysis built on top of uniqdiff 1.1."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional, Union

from uniqdiff.engine import (
    CompareResult,
    FieldDiffResult,
    compare_file_fields,
    compare_file_fields_sorted,
    compare_files,
)


@dataclass(frozen=True)
class FieldChange:
    """One changed field for one matched key."""

    field: str
    before: Any
    after: Any


@dataclass(frozen=True)
class RowChange:
    """All changed fields for one matched key."""

    key: Any
    changes: list[FieldChange]


@dataclass(frozen=True)
class RowDiffSummary:
    """Compact summary suitable for CLI output or CI checks."""

    only_in_first: int
    only_in_second: int
    common: int
    duplicates_first: int
    duplicates_second: int
    changed_rows: int
    changed_fields: int
    skipped_duplicate_keys: int
    field_result_mode: Optional[str]
    field_truncated: bool
    backend: Optional[str]
    output: Optional[str]
    presence_output: Optional[str]


@dataclass(frozen=True)
class RowDiffResult:
    """Product-layer result that wraps engine facts and row-level changes."""

    engine_result: CompareResult
    field_result: FieldDiffResult
    summary: RowDiffSummary
    changes: list[RowChange]


def diff_csv_by_key(
    first: Path,
    second: Path,
    *,
    key: str,
    ignore_fields: Iterable[str] = (),
    columns: Optional[Iterable[str]] = None,
    output: Optional[Path] = None,
    mode: str = "auto",
    encoding: str = "utf-8-sig",
    sorted_input: bool = False,
    max_rows: Optional[int] = None,
    max_bytes: Optional[Union[str, int]] = None,
) -> RowDiffResult:
    """Compare two CSV files and report field changes for shared unique keys."""

    presence_output = None if output is None else output.with_suffix(".presence.jsonl")
    engine_result = compare_files(
        str(first),
        str(second),
        format="csv",
        encoding=encoding,
        key=key,
        mode=mode,
        result_mode="file" if presence_output is not None else "memory",
        output=None if presence_output is None else str(presence_output),
        include_common=True,
        include_duplicates=True,
    )

    field_diff = compare_file_fields_sorted if sorted_input else compare_file_fields
    field_result = field_diff(
        str(first),
        str(second),
        format="csv",
        encoding=encoding,
        key=key,
        columns=None if columns is None else tuple(columns),
        exclude_columns=(key, *tuple(ignore_fields)),
    )

    duplicate_keys = _duplicate_keys(engine_result, key=key)
    changes = _row_changes(
        field_result,
        skipped_keys=duplicate_keys,
        max_rows=max_rows,
    )

    if output is not None:
        output_truncated = _write_changes_jsonl(output, changes, max_bytes=max_bytes)
    else:
        output_truncated = False

    summary = RowDiffSummary(
        only_in_first=engine_result.stats.only_in_first_count,
        only_in_second=engine_result.stats.only_in_second_count,
        common=engine_result.stats.common_count,
        duplicates_first=engine_result.stats.duplicate_first_count,
        duplicates_second=engine_result.stats.duplicate_second_count,
        changed_rows=len(changes),
        changed_fields=sum(len(change.changes) for change in changes),
        skipped_duplicate_keys=len(duplicate_keys),
        field_result_mode=field_result.metadata.get("result_mode"),
        field_truncated=field_result.stats.truncated or output_truncated,
        backend=engine_result.metadata.get("backend"),
        output=None if output is None else str(output),
        presence_output=None if presence_output is None else str(presence_output),
    )
    return RowDiffResult(
        engine_result=engine_result,
        field_result=field_result,
        summary=summary,
        changes=changes,
    )


def _duplicate_keys(result: CompareResult, *, key: str) -> set[Any]:
    duplicate_keys = set()
    for section in ("duplicates_first", "duplicates_second"):
        for row in result.iter_section(section):
            if isinstance(row, dict) and key in row:
                duplicate_keys.add(row[key])
    return duplicate_keys


def _row_changes(
    field_result: FieldDiffResult,
    *,
    skipped_keys: set[Any],
    max_rows: Optional[int],
) -> list[RowChange]:
    changes: list[RowChange] = []
    for row in field_result.rows:
        row_key = row["key"]
        if row_key in skipped_keys:
            continue
        if max_rows is not None and len(changes) >= max_rows:
            break
        changes.append(
            RowChange(
                key=row_key,
                changes=[
                    FieldChange(
                        field=change["field"],
                        before=change.get("left"),
                        after=change.get("right"),
                    )
                    for change in row.get("changes", [])
                ],
            )
        )
    return changes


def _write_changes_jsonl(
    path: Path,
    changes: list[RowChange],
    *,
    max_bytes: Optional[Union[str, int]],
) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    byte_limit = _parse_byte_limit(max_bytes)
    bytes_written = 0
    truncated = False
    with path.open("w", encoding="utf-8", newline="") as file:
        for change in changes:
            line = json.dumps(
                {"section": "changed", "value": asdict(change)},
                ensure_ascii=False,
                separators=(",", ":"),
            ) + "\n"
            line_size = len(line.encode("utf-8"))
            if byte_limit is not None and bytes_written + line_size > byte_limit:
                truncated = True
                break
            file.write(line)
            bytes_written += line_size
    return truncated


def _parse_byte_limit(value: Optional[Union[str, int]]) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    text = value.strip().lower()
    multipliers = {"kb": 1024, "mb": 1024**2, "gb": 1024**3}
    for suffix, multiplier in multipliers.items():
        if text.endswith(suffix):
            return int(float(text[: -len(suffix)].strip()) * multiplier)
    return int(text)
