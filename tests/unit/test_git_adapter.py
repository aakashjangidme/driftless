"""Unit tests for Git adapter following AAA pattern."""

from unittest.mock import MagicMock, patch

from driftless.git.adapter import GitAdapter


def _mock_run(stdout: str = "", returncode: int = 0) -> MagicMock:
    mock = MagicMock()
    mock.stdout = stdout
    mock.returncode = returncode
    mock.stderr = ""
    return mock


class TestGitAdapter:
    def test_is_repo_returns_true_when_git_inside_work_tree(self, tmp_path):
        # Arrange
        adapter = GitAdapter(tmp_path)

        # Act
        with patch(
            "driftless.git.adapter.subprocess.run", return_value=_mock_run("true\n", 0)
        ):
            is_repo = adapter.is_repo()

        # Assert
        assert is_repo is True

    def test_is_repo_returns_false_when_command_fails(self, tmp_path):
        # Arrange
        adapter = GitAdapter(tmp_path)

        # Act
        with patch("driftless.git.adapter.subprocess.run", return_value=_mock_run("", 128)):
            is_repo = adapter.is_repo()

        # Assert
        assert is_repo is False

    def test_is_repo_returns_false_when_stdout_not_true(self, tmp_path):
        # Arrange
        adapter = GitAdapter(tmp_path)

        # Act
        with patch(
            "driftless.git.adapter.subprocess.run", return_value=_mock_run("false\n", 0)
        ):
            is_repo = adapter.is_repo()

        # Assert
        assert is_repo is False

    def test_root_returns_path_object(self, tmp_path):
        # Arrange
        adapter = GitAdapter(tmp_path)

        # Act
        with patch(
            "driftless.git.adapter.subprocess.run",
            return_value=_mock_run(f"{tmp_path}\n", 0),
        ):
            root = adapter.root()

        # Assert
        assert root == tmp_path

    def test_branch_returns_active_branch_name(self, tmp_path):
        # Arrange
        adapter = GitAdapter(tmp_path)

        # Act
        with patch(
            "driftless.git.adapter.subprocess.run",
            return_value=_mock_run("feature/oauth\n", 0),
        ):
            branch_name = adapter.branch()

        # Assert
        assert branch_name == "feature/oauth"

    def test_branch_symbolic_ref_fallback(self, tmp_path):
        # Arrange
        adapter = GitAdapter(tmp_path)

        def side_effect(cmd, **kwargs):
            if "rev-parse" in cmd:
                return _mock_run("", 128)
            return _mock_run("main\n", 0)

        # Act
        with patch("driftless.git.adapter.subprocess.run", side_effect=side_effect):
            branch_name = adapter.branch()

        # Assert
        assert branch_name == "main"

    def test_branch_default_main_fallback(self, tmp_path):
        # Arrange
        adapter = GitAdapter(tmp_path)

        # Act: Both rev-parse and symbolic-ref fail
        with patch("driftless.git.adapter.subprocess.run", return_value=_mock_run("", 128)):
            branch_name = adapter.branch()

        # Assert
        assert branch_name == "main"

    def test_commit_returns_short_sha(self, tmp_path):
        # Arrange
        adapter = GitAdapter(tmp_path)

        # Act
        with patch(
            "driftless.git.adapter.subprocess.run", return_value=_mock_run("a1b2c3d\n", 0)
        ):
            commit_sha = adapter.commit()

        # Assert
        assert commit_sha == "a1b2c3d"

    def test_commit_returns_none_when_no_commits(self, tmp_path):
        # Arrange
        adapter = GitAdapter(tmp_path)

        # Act
        with patch("driftless.git.adapter.subprocess.run", return_value=_mock_run("", 128)):
            commit_sha = adapter.commit()

        # Assert
        assert commit_sha == "none"

    def test_is_clean_returns_true_when_porcelain_empty(self, tmp_path):
        # Arrange
        adapter = GitAdapter(tmp_path)

        # Act
        with patch("driftless.git.adapter.subprocess.run", return_value=_mock_run("", 0)):
            clean = adapter.is_clean()

        # Assert
        assert clean is True

    def test_is_clean_returns_false_when_porcelain_dirty(self, tmp_path):
        # Arrange
        adapter = GitAdapter(tmp_path)

        # Act
        with patch(
            "driftless.git.adapter.subprocess.run",
            return_value=_mock_run(" M src/main.py\n", 0),
        ):
            clean = adapter.is_clean()

        # Assert
        assert clean is False

    def test_status_summary_returns_unavailable_when_not_repo(self, tmp_path):
        # Arrange
        adapter = GitAdapter(tmp_path)
        with patch.object(adapter, "is_repo", return_value=False):
            # Act
            summary = adapter.status_summary()

        # Assert
        assert summary == {"available": False}

    def test_status_summary_returns_full_dict_when_repo(self, tmp_path):
        # Arrange
        adapter = GitAdapter(tmp_path)
        with (
            patch.object(adapter, "is_repo", return_value=True),
            patch.object(adapter, "branch", return_value="main"),
            patch.object(adapter, "commit", return_value="a1b2c3d"),
            patch.object(adapter, "is_clean", return_value=True),
        ):
            # Act
            summary = adapter.status_summary()

        # Assert
        assert summary == {
            "available": True,
            "branch": "main",
            "commit": "a1b2c3d",
            "clean": True,
        }
