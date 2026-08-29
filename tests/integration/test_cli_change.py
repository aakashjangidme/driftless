"""Integration unit tests for driftless change subcommands following AAA pattern."""

import json

from typer.testing import CliRunner

from driftless.cli.main import app

runner = CliRunner()


class TestCliChangeCreate:
    def test_change_create_fails_when_openspec_missing(
        self, tmp_path, monkeypatch, mocker
    ):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch(
            "driftless.cli.change.OpenSpecAdapter.detect", return_value=(False, "")
        )

        # Act
        result = runner.invoke(app, ["change", "create", "my-change"])

        # Assert
        assert result.exit_code == 1
        assert "OpenSpec not found." in result.output

    def test_change_create_fails_when_openspec_not_initialized(
        self, tmp_path, monkeypatch, mocker
    ):
        # Arrange
        monkeypatch.chdir(tmp_path)
        from driftless.work import service as ws

        mocker.patch(
            "driftless.cli.change.work_service.GitAdapter.is_repo", return_value=False
        )
        ws.create_work("Task", repo_root=tmp_path)

        mocker.patch(
            "driftless.cli.change.OpenSpecAdapter.detect", return_value=(True, "1.11.0")
        )
        mocker.patch(
            "driftless.cli.change.OpenSpecAdapter.is_initialized", return_value=False
        )

        # Act
        result = runner.invoke(app, ["change", "create", "my-change"])

        # Assert
        assert result.exit_code == 1
        assert "OpenSpec not initialized in this project." in result.output

    def test_change_create_handles_create_change_exception(
        self, tmp_path, monkeypatch, mocker
    ):
        # Arrange
        monkeypatch.chdir(tmp_path)
        from driftless.work import service as ws

        mocker.patch(
            "driftless.cli.change.work_service.GitAdapter.is_repo", return_value=False
        )
        ws.create_work("Task", repo_root=tmp_path)

        mocker.patch(
            "driftless.cli.change.OpenSpecAdapter.detect", return_value=(True, "1.11.0")
        )
        mocker.patch(
            "driftless.cli.change.OpenSpecAdapter.is_initialized", return_value=True
        )
        mocker.patch(
            "driftless.cli.change.OpenSpecAdapter.create_change",
            side_effect=Exception("OpenSpec disk error"),
        )

        # Act
        result = runner.invoke(app, ["change", "create", "my-change"])

        # Assert
        assert result.exit_code == 1
        assert "Failed to create OpenSpec change: OpenSpec disk error" in result.output

    def test_change_create_human_output_and_transition(
        self, tmp_path, monkeypatch, mocker
    ):
        # Arrange
        monkeypatch.chdir(tmp_path)
        from driftless.work import service as ws

        mocker.patch(
            "driftless.cli.change.work_service.GitAdapter.is_repo", return_value=False
        )
        ws.create_work("Task", repo_root=tmp_path)

        mocker.patch(
            "driftless.cli.change.OpenSpecAdapter.detect", return_value=(True, "1.11.0")
        )
        mocker.patch(
            "driftless.cli.change.OpenSpecAdapter.is_initialized", return_value=True
        )
        mocker.patch(
            "driftless.cli.change.OpenSpecAdapter.create_change",
            return_value={"name": "my-change"},
        )

        # Act
        result = runner.invoke(app, ["change", "create", "my-change"])

        # Assert
        assert result.exit_code == 0
        assert "Created OpenSpec change 'my-change'" in result.output

    def test_change_create_handles_transition_exception(
        self, tmp_path, monkeypatch, mocker
    ):
        # Arrange
        monkeypatch.chdir(tmp_path)
        from driftless.work import service as ws

        mocker.patch(
            "driftless.cli.change.work_service.GitAdapter.is_repo", return_value=False
        )
        ws.create_work("Task", repo_root=tmp_path)

        mocker.patch(
            "driftless.cli.change.OpenSpecAdapter.detect", return_value=(True, "1.11.0")
        )
        mocker.patch(
            "driftless.cli.change.OpenSpecAdapter.is_initialized", return_value=True
        )
        mocker.patch(
            "driftless.cli.change.OpenSpecAdapter.create_change",
            return_value={"name": "my-change"},
        )
        mocker.patch(
            "driftless.cli.change.work_service.transition",
            side_effect=ValueError("Disallowed"),
        )

        # Act
        result = runner.invoke(app, ["change", "create", "my-change", "--json"])

        # Assert
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["openspec_change"] == "my-change"


class TestCliChangeStatus:
    def test_change_status_no_change_provided_and_no_linked_change(
        self, tmp_path, monkeypatch, mocker
    ):
        # Arrange
        monkeypatch.chdir(tmp_path)
        from driftless.work import service as ws

        mocker.patch(
            "driftless.cli.change.work_service.GitAdapter.is_repo", return_value=False
        )
        ws.create_work("Task without change", repo_root=tmp_path)

        mocker.patch(
            "driftless.cli.change.OpenSpecAdapter.detect", return_value=(True, "1.11.0")
        )

        # Act
        result = runner.invoke(app, ["change", "status"])

        # Assert
        assert result.exit_code == 1
        assert (
            "No change name provided and no linked change in active work."
            in result.output
        )

    def test_change_status_human_output(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        from driftless.work import service as ws

        mocker.patch(
            "driftless.cli.change.work_service.GitAdapter.is_repo", return_value=False
        )
        work = ws.create_work("Task", repo_root=tmp_path)
        ws.link_openspec_change(work, "my-change", repo_root=tmp_path)

        mocker.patch(
            "driftless.cli.change.OpenSpecAdapter.detect", return_value=(True, "1.11.0")
        )
        mocker.patch(
            "driftless.cli.change.OpenSpecAdapter.status", return_value={"status": "ready"}
        )

        # Act
        result = runner.invoke(app, ["change", "status"])

        # Assert
        assert result.exit_code == 0
        assert "OpenSpec Change: my-change" in result.output


class TestCliChangeValidate:
    def test_change_validate_human_output_passed(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        from driftless.work import service as ws

        mocker.patch(
            "driftless.cli.change.work_service.GitAdapter.is_repo", return_value=False
        )
        work = ws.create_work("Task", repo_root=tmp_path)
        ws.link_openspec_change(work, "my-change", repo_root=tmp_path)

        mocker.patch(
            "driftless.cli.change.OpenSpecAdapter.detect", return_value=(True, "1.11.0")
        )
        mocker.patch(
            "driftless.cli.change.OpenSpecAdapter.validate", return_value={"passed": True}
        )

        # Act
        result = runner.invoke(app, ["change", "validate"])

        # Assert
        assert result.exit_code == 0
        assert "PASS" in result.output

    def test_change_validate_human_output_failed_with_errors(
        self, tmp_path, monkeypatch, mocker
    ):
        # Arrange
        monkeypatch.chdir(tmp_path)
        from driftless.work import service as ws

        mocker.patch(
            "driftless.cli.change.work_service.GitAdapter.is_repo", return_value=False
        )
        work = ws.create_work("Task", repo_root=tmp_path)
        ws.link_openspec_change(work, "my-change", repo_root=tmp_path)

        mocker.patch(
            "driftless.cli.change.OpenSpecAdapter.detect", return_value=(True, "1.11.0")
        )
        mocker.patch(
            "driftless.cli.change.OpenSpecAdapter.validate",
            return_value={"passed": False, "errors": ["Syntax error in spec"]},
        )

        # Act
        result = runner.invoke(app, ["change", "validate"])

        # Assert
        assert result.exit_code == 0
        assert "FAIL" in result.output
        assert "Syntax error in spec" in result.output
