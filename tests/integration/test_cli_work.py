"""Integration unit tests for driftless work subcommands following AAA pattern."""

import json

from typer.testing import CliRunner

from driftless.cli.main import app

runner = CliRunner()


class TestCliWorkCreate:
    def test_work_create_handles_service_exception(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch(
            "driftless.cli.work.work_service.create_work",
            side_effect=Exception("Disk full"),
        )

        # Act
        result = runner.invoke(app, ["work", "create", "Failed Work"])

        # Assert
        assert result.exit_code == 1
        assert "Failed to create work: Disk full" in result.output

    def test_work_create_returns_none_when_error_hint_mocked(
        self, tmp_path, monkeypatch, mocker
    ):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch(
            "driftless.cli.work.work_service.create_work",
            side_effect=Exception("Disk full"),
        )
        mocker.patch("driftless.cli.work.renderer.error_with_hint", return_value=None)

        # Act
        result = runner.invoke(app, ["work", "create", "Failed Work"])

        # Assert
        assert result.exit_code == 0

    def test_work_create_human_output(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch(
            "driftless.cli.work.work_service.GitAdapter.is_repo", return_value=False
        )

        # Act
        result = runner.invoke(app, ["work", "create", "Human Work"])

        # Assert
        assert result.exit_code == 0
        assert "Created Work W-0001" in result.output

    def test_work_create_json_output(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch(
            "driftless.cli.work.work_service.GitAdapter.is_repo", return_value=False
        )

        # Act
        result = runner.invoke(
            app, ["work", "create", "JSON Work", "--type", "bug", "--json"]
        )

        # Assert
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["title"] == "JSON Work"
        assert data["type"] == "bug"


class TestCliWorkList:
    def test_work_list_empty_human_output(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch("driftless.cli.work.work_service.list_works", return_value=[])

        # Act
        result = runner.invoke(app, ["work", "list"])

        # Assert
        assert result.exit_code == 0
        assert "No work found. Run: driftless work create <description>" in result.output

    def test_work_list_json_output(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch(
            "driftless.cli.work.work_service.GitAdapter.is_repo", return_value=False
        )
        runner.invoke(app, ["work", "create", "Task 1"])

        # Act
        result = runner.invoke(app, ["work", "list", "--json"])

        # Assert
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 1

    def test_work_list_human_table(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch(
            "driftless.cli.work.work_service.GitAdapter.is_repo", return_value=False
        )
        runner.invoke(app, ["work", "create", "Task 1"])

        # Act
        result = runner.invoke(app, ["work", "list"])

        # Assert
        assert result.exit_code == 0
        assert "Driftless Works" in result.output


class TestCliWorkShow:
    def test_work_show_human_mode(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch(
            "driftless.cli.work.work_service.GitAdapter.is_repo", return_value=False
        )
        runner.invoke(app, ["work", "create", "Task 1"])

        # Act
        result = runner.invoke(app, ["work", "show", "W-0001"])

        # Assert
        assert result.exit_code == 0
        assert "Driftless · W-0001" in result.output

    def test_work_show_json_mode(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch(
            "driftless.cli.work.work_service.GitAdapter.is_repo", return_value=False
        )
        runner.invoke(app, ["work", "create", "Task 1"])

        # Act
        result = runner.invoke(app, ["work", "show", "W-0001", "--json"])

        # Assert
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == "W-0001"

    def test_work_show_invalid_id_exits_with_error(self, tmp_path, monkeypatch):
        # Arrange
        monkeypatch.chdir(tmp_path)

        # Act
        result = runner.invoke(app, ["work", "show", "W-9999"])

        # Assert
        assert result.exit_code == 1
        assert "Work 'W-9999' not found." in result.output

    def test_work_show_returns_early_when_resolve_work_returns_none(
        self, tmp_path, monkeypatch, mocker
    ):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch("driftless.cli.work.resolve_work", return_value=None)

        # Act
        result = runner.invoke(app, ["work", "show", "W-0001"])

        # Assert
        assert result.exit_code == 0
