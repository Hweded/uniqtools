from __future__ import annotations

import shutil
from pathlib import Path

from uniqtools_cli.cli import main


def test_unified_cli_dispatches_profile_command(capsys):
    workspace = _workspace("profile")
    try:
        users = workspace / "users.csv"
        users.write_text("id,email\n1,ann@example.com\n", encoding="utf-8")

        exit_code = main(["profile", "file", str(users), "--key", "id"])

        captured = capsys.readouterr()
        assert exit_code == 0
        assert '"row_count": 1' in captured.out
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_unified_cli_dispatches_check_command(capsys):
    workspace = _workspace("check")
    try:
        users = workspace / "users.csv"
        users.write_text("id,email\n1,ann@example.com\n1,ann2@example.com\n", encoding="utf-8")

        exit_code = main(["check", "file", str(users), "--key", "id", "--fail-on-duplicates"])

        captured = capsys.readouterr()
        assert exit_code == 1
        assert '"duplicate_key_count": 1' in captured.out
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def _workspace(name: str) -> Path:
    path = Path.cwd() / ".tmp" / "uniqtools_cli_tests" / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path
