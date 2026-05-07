"""CI-friendly checks built on top of uniqdiff."""

from uniqcheck.checks import (
    CompareCheckResult,
    FileCheckResult,
    SchemaCheckResult,
    check_csv_file,
    compare_csv_by_key,
    compare_csv_schema,
)

__all__ = [
    "CompareCheckResult",
    "FileCheckResult",
    "SchemaCheckResult",
    "check_csv_file",
    "compare_csv_by_key",
    "compare_csv_schema",
]
