"""CI-friendly checks built on top of uniqdiff."""

from uniqcheck.checks import (
    CompareCheckResult,
    FileCheckResult,
    check_csv_file,
    compare_csv_by_key,
)

__all__ = [
    "CompareCheckResult",
    "FileCheckResult",
    "check_csv_file",
    "compare_csv_by_key",
]
