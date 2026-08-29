"""Integration unit tests for main CLI commands following AAA pattern."""

import json

from typer.testing import CliRunner

from driftless.cli.main import app
from driftless.work import service as ws
from driftless.work.models import WorkStatus

runner = CliRunner()


class TestCliMainCallback:
    def test_main_callback_version_flag(self):
        # Arrange & Act
        result = runner.invoke(app, ["--version"])

        # Assert
        assert result.exit_code == 0
        assert "driftless 0.1.0" in result.output

    def test_main_callback_verbose_flag(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch(
            "driftless.cli.main.GitAdapter.status_summary",
            return_value={"available": True, "branch": "main", "clean": True},
        )

        # Act
        result = runner.invoke(app, ["--verbose", "status"])

        # Assert
        assert result.exit_code == 0


class TestCliMainInit:
    def test_init_fails_outside_git_repo(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch("driftless.cli.main.GitAdapter.is_repo", return_value=False)

        # Act
        result = runner.invoke(app, ["init"])

        # Assert
        assert result.exit_code == 1
        assert "Not inside a git repository." in result.output

    def test_init_fails_when_openspec_missing(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch("driftless.cli.main.GitAdapter.is_repo", return_value=True)
        mocker.patch("driftless.cli.main.GitAdapter.root", return_value=tmp_path)
        mocker.patch("driftless.cli.main.GitAdapter.branch", return_value="main")
        mocker.patch("driftless.cli.main.OpenSpecAdapter.detect", return_value=(False, ""))

        # Act
        result = runner.invoke(app, ["init"])

        # Assert
        assert result.exit_code == 1
        assert "OpenSpec not found." in result.output

    def test_init_fails_when_openspec_init_raises(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch("driftless.cli.main.GitAdapter.is_repo", return_value=True)
        mocker.patch("driftless.cli.main.GitAdapter.root", return_value=tmp_path)
        mocker.patch("driftless.cli.main.GitAdapter.branch", return_value="main")
        mocker.patch(
            "driftless.cli.main.OpenSpecAdapter.detect", return_value=(True, "1.11.0")
        )
        mocker.patch(
            "driftless.cli.main.OpenSpecAdapter.is_initialized", return_value=False
        )
        mocker.patch(
            "driftless.cli.main.OpenSpecAdapter.init",
            side_effect=Exception("OpenSpec init failed"),
        )

        # Act
        result = runner.invoke(app, ["init"])

        # Assert
        assert result.exit_code == 1
        assert "OpenSpec initialization failed" in result.output

    def test_init_success_full_flow(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch("driftless.cli.main.GitAdapter.is_repo", return_value=True)
        mocker.patch("driftless.cli.main.GitAdapter.root", return_value=tmp_path)
        mocker.patch("driftless.cli.main.GitAdapter.branch", return_value="main")
        mocker.patch(
            "driftless.cli.main.OpenSpecAdapter.detect", return_value=(True, "1.11.0")
        )
        mocker.patch(
            "driftless.cli.main.OpenSpecAdapter.is_initialized", return_value=False
        )
        mocker.patch("driftless.cli.main.OpenSpecAdapter.init", return_value=None)

        # Act
        result = runner.invoke(app, ["init"])

        # Assert
        assert result.exit_code == 0
        assert "Driftless initialized." in result.output

    def test_init_success_when_openspec_already_initialized(
        self, tmp_path, monkeypatch, mocker
    ):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch("driftless.cli.main.GitAdapter.is_repo", return_value=True)
        mocker.patch("driftless.cli.main.GitAdapter.root", return_value=tmp_path)
        mocker.patch("driftless.cli.main.GitAdapter.branch", return_value="main")
        mocker.patch(
            "driftless.cli.main.OpenSpecAdapter.detect", return_value=(True, "1.11.0")
        )
        mocker.patch("driftless.cli.main.OpenSpecAdapter.is_initialized", return_value=True)

        # Act
        result = runner.invoke(app, ["init"])

        # Assert
        assert result.exit_code == 0
        assert "OpenSpec already initialized" in result.output


class TestCliMainStatus:
    def test_status_when_no_active_work(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch(
            "driftless.cli.main.GitAdapter.status_summary",
            return_value={"available": True, "branch": "main", "clean": True},
        )

        # Act
        result = runner.invoke(app, ["status", "--json"])

        # Assert
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["work"] == {}
        assert "create work with" in data["message"]

    def test_status_with_explicit_invalid_work_id(self, tmp_path, monkeypatch):
        # Arrange
        monkeypatch.chdir(tmp_path)

        # Act
        result = runner.invoke(app, ["status", "--work", "W-9999"])

        # Assert
        assert result.exit_code == 1
        assert "Work 'W-9999' not found." in result.output

    def test_status_when_openspec_not_initialized(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch(
            "driftless.cli.main.GitAdapter.status_summary",
            return_value={"available": True, "branch": "main", "clean": True},
        )
        mocker.patch(
            "driftless.cli.main.OpenSpecAdapter.detect", return_value=(True, "1.11.0")
        )
        mocker.patch(
            "driftless.cli.main.OpenSpecAdapter.is_initialized", return_value=False
        )
        mocker.patch("driftless.cli.main.GitAdapter.is_repo", return_value=False)

        work = ws.create_work("Task", repo_root=tmp_path)
        ws.link_openspec_change(work, "my-change", repo_root=tmp_path)

        # Act
        result = runner.invoke(app, ["status", "--json"])

        # Assert
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["openspec"]["status"] == "not-initialized"

    def test_status_human_mode(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch(
            "driftless.cli.main.GitAdapter.status_summary",
            return_value={"available": True, "branch": "main", "clean": True},
        )
        mocker.patch(
            "driftless.cli.main.OpenSpecAdapter.detect", return_value=(True, "1.11.0")
        )
        mocker.patch("driftless.cli.main.OpenSpecAdapter.is_initialized", return_value=True)
        mocker.patch(
            "driftless.cli.main.OpenSpecAdapter.status", return_value={"status": "ready"}
        )
        mocker.patch("driftless.cli.main.GitAdapter.is_repo", return_value=False)

        work = ws.create_work("Task", repo_root=tmp_path)
        ws.link_openspec_change(work, "my-change", repo_root=tmp_path)

        # Act
        result = runner.invoke(app, ["status"])

        # Assert
        assert result.exit_code == 0
        assert "Driftless · W-0001" in result.output


class TestCliMainVerify:
    def test_verify_fails_when_no_active_work(self, tmp_path, monkeypatch):
        # Arrange
        monkeypatch.chdir(tmp_path)

        # Act
        result = runner.invoke(app, ["verify"])

        # Assert
        assert result.exit_code == 1
        assert "No active work found." in result.output

    def test_verify_fails_when_work_id_not_found(self, tmp_path, monkeypatch):
        # Arrange
        monkeypatch.chdir(tmp_path)

        # Act
        result = runner.invoke(app, ["verify", "--work", "W-9999"])

        # Assert
        assert result.exit_code == 1
        assert "Work 'W-9999' not found." in result.output

    def test_verify_fails_when_git_not_available(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch("driftless.cli.main.GitAdapter.is_repo", return_value=False)
        ws.create_work("Task", repo_root=tmp_path)
        mocker.patch(
            "driftless.cli.main.GitAdapter.status_summary",
            return_value={"available": False},
        )

        # Act
        result = runner.invoke(app, ["verify", "--json"])

        # Assert
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["status"] == "fail"
        assert "Not inside a git repository." in data["errors"]

    def test_verify_openspec_validation_failure_human(
        self, tmp_path, monkeypatch, mocker
    ):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch("driftless.cli.main.GitAdapter.is_repo", return_value=False)
        work = ws.create_work("Task", repo_root=tmp_path)
        ws.link_openspec_change(work, "my-change", repo_root=tmp_path)

        mocker.patch(
            "driftless.cli.main.GitAdapter.status_summary",
            return_value={"available": True, "branch": "main", "clean": True},
        )
        mocker.patch(
            "driftless.cli.main.OpenSpecAdapter.detect", return_value=(True, "1.11.0")
        )
        mocker.patch("driftless.cli.main.OpenSpecAdapter.is_initialized", return_value=True)
        mocker.patch(
            "driftless.cli.main.OpenSpecAdapter.validate",
            return_value={"passed": False, "status": "fail", "errors": ["Spec error"]},
        )

        # Act
        result = runner.invoke(app, ["verify"])

        # Assert
        assert result.exit_code == 1
        assert "FAIL" in result.output
        assert "OpenSpec validation failed for change 'my-change'." in result.output

    def test_verify_no_change_linked_warning(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch("driftless.cli.main.GitAdapter.is_repo", return_value=False)
        ws.create_work("Task without change", repo_root=tmp_path)

        mocker.patch(
            "driftless.cli.main.GitAdapter.status_summary",
            return_value={"available": True, "branch": "main", "clean": True},
        )

        # Act
        result = runner.invoke(app, ["verify", "--json"])

        # Assert
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "No OpenSpec change linked to this work." in data["warnings"][0]

    def test_verify_work_already_done(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch("driftless.cli.main.GitAdapter.is_repo", return_value=False)
        work = ws.create_work("Task", repo_root=tmp_path)
        done_work = work.model_copy(update={"status": WorkStatus.DONE})
        ws.store.save(done_work, repo_root=tmp_path)

        mocker.patch(
            "driftless.cli.main.GitAdapter.status_summary",
            return_value={"available": True, "branch": "main", "clean": True},
        )

        # Act
        result = runner.invoke(app, ["verify", "--work", work.id, "--json"])

        # Assert
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["status"] == "fail"
        assert f"Work {work.id} is already DONE." in data["errors"]


class TestCliMainReviewAndFinish:
    def test_review_human_mode_success(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        work = ws.create_work("Task", repo_root=tmp_path)
        work = work.transition_to(WorkStatus.IMPLEMENTING)
        ws.store.save(work, tmp_path)

        # Act
        result = runner.invoke(app, ["review"])

        # Assert
        assert result.exit_code == 0
        assert "Work W-0001 moved to REVIEW" in result.output

    def test_finish_human_mode_success(self, tmp_path, monkeypatch, mocker):
        # Arrange
        monkeypatch.chdir(tmp_path)
        mocker.patch("driftless.cli.main.GitAdapter.is_repo", return_value=False)
        work = ws.create_work("Task", repo_root=tmp_path)
        review_work = work.model_copy(
            update={"status": WorkStatus.REVIEW, "openspec_change": "my-change"}
        )
        ws.store.save(review_work, repo_root=tmp_path)

        mocker.patch(
            "driftless.cli.main.OpenSpecAdapter.detect", return_value=(True, "1.11.0")
        )
        mocker.patch("driftless.cli.main.OpenSpecAdapter.is_initialized", return_value=True)
        mocker.patch("driftless.cli.main.OpenSpecAdapter.archive", return_value=None)

        # Act
        result = runner.invoke(app, ["finish"])

        # Assert
        assert result.exit_code == 0
        assert "Work W-0001 is DONE. 🎉" in result.output
