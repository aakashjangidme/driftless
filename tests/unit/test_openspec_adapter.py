"""Unit tests for OpenSpec adapter following AAA pattern."""

import json
from unittest.mock import MagicMock, patch

import pytest

from driftless.openspec.adapter import OpenSpecAdapter, OpenSpecError, OpenSpecNotFound


def _mock_run(stdout: str = "", returncode: int = 0, stderr: str = "") -> MagicMock:
    mock = MagicMock()
    mock.stdout = stdout
    mock.returncode = returncode
    mock.stderr = stderr
    return mock


class TestOpenSpecAdapterDetect:
    def test_detect_returns_available_and_version(self, tmp_path):
        # Arrange
        adapter = OpenSpecAdapter(tmp_path)

        # Act
        with patch(
            "driftless.openspec.adapter.subprocess.run",
            return_value=_mock_run("1.11.0\n", 0),
        ):
            available, version = adapter.detect()

        # Assert
        assert available is True
        assert version == "1.11.0"

    def test_detect_returns_false_on_command_failure(self, tmp_path):
        # Arrange
        adapter = OpenSpecAdapter(tmp_path)

        # Act
        with patch(
            "driftless.openspec.adapter.subprocess.run", return_value=_mock_run("", 127)
        ):
            available, version = adapter.detect()

        # Assert
        assert available is False
        assert version == ""


class TestOpenSpecAdapterIsInitialized:
    def test_is_initialized_returns_true_when_openspec_dir_exists(self, tmp_path):
        # Arrange
        (tmp_path / "openspec").mkdir()
        adapter = OpenSpecAdapter(tmp_path)

        # Act
        initialized = adapter.is_initialized()

        # Assert
        assert initialized is True

    def test_is_initialized_returns_false_when_no_openspec_dir(self, tmp_path):
        # Arrange
        adapter = OpenSpecAdapter(tmp_path)

        # Act
        initialized = adapter.is_initialized()

        # Assert
        assert initialized is False


class TestOpenSpecAdapterCommands:
    def test_init_executes_openspec_init(self, tmp_path):
        # Arrange
        adapter = OpenSpecAdapter(tmp_path)

        # Act
        with patch(
            "driftless.openspec.adapter.subprocess.run", return_value=_mock_run("", 0)
        ) as mock_run:
            adapter.init(tools="claude")

        # Assert
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "init" in args
        assert "--tools" in args

    def test_create_change_with_description(self, tmp_path):
        # Arrange
        adapter = OpenSpecAdapter(tmp_path)
        payload = {"name": "add-oauth", "status": "created"}

        # Act
        with patch(
            "driftless.openspec.adapter.subprocess.run",
            return_value=_mock_run(json.dumps(payload), 0),
        ):
            res = adapter.create_change("add-oauth", description="OAuth Login Flow")

        # Assert
        assert res["name"] == "add-oauth"

    def test_create_change_without_description(self, tmp_path):
        # Arrange
        adapter = OpenSpecAdapter(tmp_path)

        # Act
        with patch(
            "driftless.openspec.adapter.subprocess.run",
            return_value=_mock_run("Created", 0),
        ):
            res = adapter.create_change("add-oauth")

        # Assert
        assert res["name"] == "add-oauth"

    def test_status_returns_parsed_json(self, tmp_path):
        # Arrange
        adapter = OpenSpecAdapter(tmp_path)
        payload = {"changeName": "add-oauth", "status": "ready"}

        # Act
        with patch(
            "driftless.openspec.adapter.subprocess.run",
            return_value=_mock_run(json.dumps(payload), 0),
        ):
            res = adapter.status("add-oauth")

        # Assert
        assert res["changeName"] == "add-oauth"

    def test_status_returns_raw_on_non_json(self, tmp_path):
        # Arrange
        adapter = OpenSpecAdapter(tmp_path)

        # Act
        with patch(
            "driftless.openspec.adapter.subprocess.run",
            return_value=_mock_run("Non JSON status", 0),
        ):
            res = adapter.status("add-oauth")

        # Assert
        assert res == {"raw": "Non JSON status", "available": True}

    def test_status_returns_error_dict_on_failure(self, tmp_path):
        # Arrange
        adapter = OpenSpecAdapter(tmp_path)

        # Act
        with patch(
            "driftless.openspec.adapter.subprocess.run",
            return_value=_mock_run("", 1, "Change not found"),
        ):
            res = adapter.status("invalid-change")

        # Assert
        assert res == {"error": "Change not found", "available": False}

    def test_validate_success(self, tmp_path):
        # Arrange
        adapter = OpenSpecAdapter(tmp_path)
        payload = {"passed": True}

        # Act
        with patch(
            "driftless.openspec.adapter.subprocess.run",
            return_value=_mock_run(json.dumps(payload), 0),
        ):
            res = adapter.validate("add-oauth")

        # Assert
        assert res["passed"] is True
        assert res["exit_code"] == 0

    def test_validate_json_decode_error_fallback(self, tmp_path):
        # Arrange
        adapter = OpenSpecAdapter(tmp_path)

        # Act
        with patch(
            "driftless.openspec.adapter.subprocess.run",
            return_value=_mock_run("Plain text validate output", 1),
        ):
            res = adapter.validate("add-oauth")

        # Assert
        assert res["raw"] == "Plain text validate output"
        assert res["passed"] is False
        assert res["exit_code"] == 1

    def test_archive_success(self, tmp_path):
        # Arrange
        adapter = OpenSpecAdapter(tmp_path)

        # Act & Assert
        with patch(
            "driftless.openspec.adapter.subprocess.run", return_value=_mock_run("", 0)
        ):
            adapter.archive("add-oauth")

    def test_change_show_success(self, tmp_path):
        # Arrange
        adapter = OpenSpecAdapter(tmp_path)
        payload = {"id": "add-oauth"}

        # Act
        with patch(
            "driftless.openspec.adapter.subprocess.run",
            return_value=_mock_run(json.dumps(payload), 0),
        ):
            res = adapter.change_show("add-oauth")

        # Assert
        assert res["id"] == "add-oauth"

    def test_change_show_error_and_raw_fallback(self, tmp_path):
        # Arrange
        adapter = OpenSpecAdapter(tmp_path)

        # Act 1: Error
        with patch(
            "driftless.openspec.adapter.subprocess.run",
            return_value=_mock_run("", 1, "Not found"),
        ):
            res_err = adapter.change_show("invalid")

        # Act 2: Non-JSON success
        with patch(
            "driftless.openspec.adapter.subprocess.run",
            return_value=_mock_run("Raw Show", 0),
        ):
            res_raw = adapter.change_show("valid")

        # Assert
        assert res_err["found"] is False
        assert res_raw["found"] is True
        assert res_raw["raw"] == "Raw Show"

    def test_list_changes_success_and_failures(self, tmp_path):
        # Arrange
        adapter = OpenSpecAdapter(tmp_path)

        # Act 1: JSON success
        with patch(
            "driftless.openspec.adapter.subprocess.run",
            return_value=_mock_run(json.dumps({"changes": []}), 0),
        ):
            res_json = adapter.list_changes()

        # Act 2: Error failure
        with patch(
            "driftless.openspec.adapter.subprocess.run",
            return_value=_mock_run("", 1, "Error list"),
        ):
            res_err = adapter.list_changes()

        # Act 3: Non-JSON success
        with patch(
            "driftless.openspec.adapter.subprocess.run",
            return_value=_mock_run("Raw List", 0),
        ):
            res_raw = adapter.list_changes()

        # Assert
        assert res_json == {"changes": []}
        assert res_err == {"error": "Error list", "changes": []}
        assert res_raw == {"raw": "Raw List"}


class TestOpenSpecNotFoundHint:
    def test_install_hint_formatting(self):
        # Arrange & Act & Assert
        assert (
            "npm install -g @fission-ai/openspec@latest"
            in OpenSpecNotFound.INSTALL_HINT
        )

    def test_run_raises_openspec_error_when_check_true(self, tmp_path):
        # Arrange
        adapter = OpenSpecAdapter(tmp_path)

        # Act & Assert
        with patch(
            "driftless.openspec.adapter.subprocess.run",
            return_value=_mock_run("", 1, "Command failed"),
        ), pytest.raises(OpenSpecError, match="OpenSpec command failed"):
            adapter._run(["invalid"], check=True)
