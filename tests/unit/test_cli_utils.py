"""Unit tests for CLI utility functions following AAA pattern."""

import pytest

from driftless.cli.utils import resolve_work
from driftless.state import store
from driftless.work.models import Work, WorkStatus


class TestResolveWork:
    def test_resolve_work_by_explicit_valid_id(self, tmp_path):
        # Arrange
        work = Work(id="W-0001", title="Explicit Work")
        store.save(work, repo_root=tmp_path)

        # Act
        resolved = resolve_work(work_id="W-0001", required=True, repo_root=tmp_path)

        # Assert
        assert resolved is not None
        assert resolved.id == "W-0001"
        assert resolved.title == "Explicit Work"

    def test_resolve_work_by_invalid_id_calls_error_with_hint(self, tmp_path):
        # Arrange & Act & Assert
        with pytest.raises(SystemExit) as exc_info:
            resolve_work(work_id="W-9999", required=True, repo_root=tmp_path)
        assert exc_info.value.code == 1

    def test_resolve_work_default_to_active_work(self, tmp_path):
        # Arrange
        work = Work(id="W-0001", title="Active Work", status=WorkStatus.IMPLEMENTING)
        store.save(work, repo_root=tmp_path)

        # Act
        resolved = resolve_work(work_id=None, required=True, repo_root=tmp_path)

        # Assert
        assert resolved is not None
        assert resolved.id == "W-0001"

    def test_resolve_work_returns_none_when_no_active_work_and_not_required(
        self, tmp_path
    ):
        # Arrange & Act
        resolved = resolve_work(work_id=None, required=False, repo_root=tmp_path)

        # Assert
        assert resolved is None

    def test_resolve_work_exits_when_no_active_work_and_required(self, tmp_path):
        # Arrange & Act & Assert
        with pytest.raises(SystemExit) as exc_info:
            resolve_work(work_id=None, required=True, repo_root=tmp_path)
        assert exc_info.value.code == 1

    def test_resolve_work_returns_none_when_error_with_hint_mocked(
        self, tmp_path, mocker
    ):
        # Arrange
        mocker.patch("driftless.cli.utils.renderer.error_with_hint", return_value=None)

        # Act 1: Invalid work_id
        res1 = resolve_work(work_id="W-9999", required=True, repo_root=tmp_path)
        # Act 2: Missing active work
        res2 = resolve_work(work_id=None, required=True, repo_root=tmp_path)

        # Assert
        assert res1 is None
        assert res2 is None
