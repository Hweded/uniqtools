from __future__ import annotations

import json
import shutil
from pathlib import Path

from uniqprofile import profile_file
from uniqprofile.cli import main


def test_profile_csv_reports_columns_empty_values_and_duplicate_keys():
    workspace = _workspace("csv")
    try:
        users = workspace / "users.csv"
        users.write_text(
            "id,email,status\n"
            "1,ann@example.com,active\n"
            "1,ann2@example.com,\n"
            "2,bob@example.com,inactive\n",
            encoding="utf-8",
        )

        result = profile_file(users, format="csv", key="id")

        assert result.row_count == 3
        assert result.columns == ["id", "email", "status"]
        assert result.empty_counts == {"id": 0, "email": 0, "status": 1}
        assert result.duplicate_key_count == 1
        assert result.duplicate_keys_sample == ["1"]
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_profile_jsonl_reports_invalid_records_and_fields():
    workspace = _workspace("jsonl")
    try:
        events = workspace / "events.jsonl"
        events.write_text(
            json.dumps({"id": "1", "status": "ok"}) + "\n"
            + "{bad json}\n"
            + json.dumps({"id": "1", "status": "", "payload": ["nested"]}) + "\n",
            encoding="utf-8",
        )

        result = profile_file(events, format="jsonl", key="id")

        assert result.row_count == 2
        assert result.invalid_record_count == 1
        assert result.columns == ["id", "payload", "status"]
        assert result.empty_counts == {"id": 0, "payload": 0, "status": 1}
        assert result.duplicate_key_count == 1
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_cli_profile_prints_json(capsys):
    workspace = _workspace("cli")
    try:
        users = workspace / "users.csv"
        users.write_text("id,email\n1,ann@example.com\n", encoding="utf-8")

        exit_code = main(["file", str(users), "--key", "id"])

        captured = capsys.readouterr()
        assert exit_code == 0
        assert '"row_count": 1' in captured.out
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def _workspace(name: str) -> Path:
    path = Path.cwd() / ".tmp" / "uniqprofile_tests" / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path
