"""End-to-end (E2E) integration test for Driftless CLI workflow following AAA pattern."""

import json
import os
import subprocess

import pytest
from typer.testing import CliRunner

from driftless.cli.main import app


@pytest.fixture
def temp_git_repo(tmp_path):
    """Create a clean temporary git repository fixture."""
    repo = tmp_path / "e2e-repo"
    repo.mkdir()

    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "E2E User"], cwd=repo, check=True)
    subprocess.run(
        ["git", "config", "user.email", "e2e@example.com"], cwd=repo, check=True
    )

    (repo / "README.md").write_text("# E2E Test Repo\n")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo, check=True)

    return repo


class TestE2EFullLifecycle:
    def test_complete_driftless_sdlc_lifecycle(self, temp_git_repo, mocker):
        # Arrange
        repo = temp_git_repo
        os.chdir(repo)

        mocker.patch(
            "driftless.openspec.adapter.OpenSpecAdapter.detect",
            return_value=(True, "1.11.0"),
        )
        mocker.patch(
            "driftless.openspec.adapter.OpenSpecAdapter.is_initialized", return_value=True
        )
        mocker.patch("driftless.openspec.adapter.OpenSpecAdapter.init", return_value=None)
        mocker.patch(
            "driftless.openspec.adapter.OpenSpecAdapter.create_change",
            return_value={"name": "add-oauth", "status": "created"},
        )
        mocker.patch(
            "driftless.openspec.adapter.OpenSpecAdapter.status",
            return_value={"status": "ready"},
        )
        mocker.patch(
            "driftless.openspec.adapter.OpenSpecAdapter.validate",
            return_value={"passed": True, "status": "pass", "exit_code": 0},
        )
        mocker.patch(
            "driftless.openspec.adapter.OpenSpecAdapter.archive", return_value=None
        )

        runner = CliRunner()

        # Act 1: driftless init
        init_res = runner.invoke(app, ["init"])

        # Assert 1
        assert init_res.exit_code == 0
        assert (repo / ".driftless").exists()
        assert (repo / "CLAUDE.md").exists()
        assert (repo / "AGENTS.md").exists()

        # Act 2: driftless work create
        create_res = runner.invoke(
            app, ["work", "create", "Add OAuth 2.0 Flow", "--json"]
        )

        # Assert 2
        assert create_res.exit_code == 0
        work_data = json.loads(create_res.output)
        assert work_data["id"] == "W-0001"
        assert work_data["title"] == "Add OAuth 2.0 Flow"

        # Act 3: driftless change create
        change_res = runner.invoke(app, ["change", "create", "add-oauth", "--json"])

        # Assert 3
        assert change_res.exit_code == 0
        change_data = json.loads(change_res.output)
        assert change_data["openspec_change"] == "add-oauth"

        # Act 4: driftless status
        status_res = runner.invoke(app, ["status", "--json"])

        # Assert 4
        assert status_res.exit_code == 0
        status_data = json.loads(status_res.output)
        assert status_data["work"]["id"] == "W-0001"
        assert status_data["work"]["openspec_change"] == "add-oauth"

        # Act 5: driftless verify
        verify_res = runner.invoke(app, ["verify", "--json"])

        # Assert 5
        assert verify_res.exit_code == 0
        verify_data = json.loads(verify_res.output)
        assert verify_data["status"] == "pass"

        # Act 6: driftless review
        review_res = runner.invoke(app, ["review", "--json"])

        # Assert 6
        assert review_res.exit_code == 0
        review_data = json.loads(review_res.output)
        assert review_data["status"] == "REVIEW"

        # Act 7: driftless finish
        finish_res = runner.invoke(app, ["finish", "--json"])

        # Assert 7
        assert finish_res.exit_code == 0
        finish_data = json.loads(finish_res.output)
        assert finish_data["work"]["status"] == "DONE"
        assert finish_data["openspec_archived"] is True
