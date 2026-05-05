from __future__ import annotations

import shutil
from pathlib import Path

from uniqcheck import check_csv_file, compare_csv_by_key
from uniqcheck.cli import main


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    columns = ["id", "email", "status"]
    lines = [",".join(columns)]
    for row in rows:
        lines.append(",".join(row[column] for column in columns))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_check_csv_file_reports_missing_columns_and_duplicates():
    workspace = _workspace("file")
    try:
        users = workspace / "users.csv"
        _write_csv(
            users,
            [
                {"id": "1", "email": "ann@example.com", "status": "active"},
                {"id": "1", "email": "ann2@example.com", "status": "active"},
                {"id": "2", "email": "bob@example.com", "status": "inactive"},
            ],
        )

        result = check_csv_file(
            users,
            key="id",
            required_columns=("email", "country"),
        )

        assert result.row_count == 3
        assert result.required_columns_missing == ["country"]
        assert result.duplicate_key_count == 1
        assert result.duplicate_keys == ["1"]
        assert not result.passed
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_compare_csv_by_key_reports_presence_counts():
    workspace = _workspace("compare")
    try:
        old_csv = workspace / "old.csv"
        new_csv = workspace / "new.csv"
        _write_csv(
            old_csv,
            [
                {"id": "1", "email": "ann@example.com", "status": "active"},
                {"id": "2", "email": "bob@example.com", "status": "active"},
            ],
        )
        _write_csv(
            new_csv,
            [
                {"id": "2", "email": "bob@example.com", "status": "active"},
                {"id": "3", "email": "cara@example.com", "status": "active"},
            ],
        )

        result = compare_csv_by_key(old_csv, new_csv, key="id")

        assert result.only_in_first == 1
        assert result.only_in_second == 1
        assert result.common == 1
        assert result.backend in {"memory", "sqlite"}
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_cli_file_returns_failure_code_for_duplicates(capsys):
    workspace = _workspace("cli-file")
    try:
        users = workspace / "users.csv"
        _write_csv(
            users,
            [
                {"id": "1", "email": "ann@example.com", "status": "active"},
                {"id": "1", "email": "ann2@example.com", "status": "active"},
            ],
        )

        exit_code = main(
            [
                "file",
                str(users),
                "--key",
                "id",
                "--fail-on-duplicates",
            ]
        )

        captured = capsys.readouterr()
        assert exit_code == 1
        assert '"duplicate_key_count": 1' in captured.out
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_cli_compare_returns_failure_code_for_added_rows(capsys):
    workspace = _workspace("cli-compare")
    try:
        old_csv = workspace / "old.csv"
        new_csv = workspace / "new.csv"
        _write_csv(old_csv, [{"id": "1", "email": "ann@example.com", "status": "active"}])
        _write_csv(
            new_csv,
            [
                {"id": "1", "email": "ann@example.com", "status": "active"},
                {"id": "2", "email": "bob@example.com", "status": "active"},
            ],
        )

        exit_code = main(
            [
                "compare",
                str(old_csv),
                str(new_csv),
                "--key",
                "id",
                "--fail-on-added",
            ]
        )

        captured = capsys.readouterr()
        assert exit_code == 1
        assert '"only_in_second": 1' in captured.out
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_check_csv_file_accepts_utf8_bom_header():
    workspace = _workspace("bom")
    try:
        users = workspace / "users.csv"
        users.write_text(
            "\ufeffid,email,status\n1,ann@example.com,active\n1,ann2@example.com,active\n",
            encoding="utf-8",
        )

        result = check_csv_file(users, key="id", required_columns=("email",))

        assert result.required_columns_missing == []
        assert result.duplicate_key_count == 1
        assert result.duplicate_keys == ["1"]
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def _workspace(name: str) -> Path:
    path = Path.cwd() / ".tmp" / "uniqcheck_tests" / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path
