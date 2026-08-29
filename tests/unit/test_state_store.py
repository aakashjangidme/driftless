"""Unit tests for state store."""

import pytest

from driftless.state import store
from driftless.work.models import Work, WorkStatus, WorkType


def _make_work(wid: str = "W-0001", title: str = "Test") -> Work:
    return Work(id=wid, title=title, type=WorkType.feature)


class TestStateStore:
    def test_save_and_load_round_trip(self, tmp_path):
        work = _make_work()
        store.save(work, repo_root=tmp_path)

        loaded = store.load("W-0001", repo_root=tmp_path)
        assert loaded.id == work.id
        assert loaded.title == work.title
        assert loaded.status == work.status

    def test_state_json_written_to_correct_path(self, tmp_path):
        work = _make_work()
        store.save(work, repo_root=tmp_path)

        expected_path = tmp_path / ".driftless" / "work" / "W-0001" / "state.json"
        assert expected_path.exists()

    def test_load_nonexistent_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            store.load("W-9999", repo_root=tmp_path)

    def test_list_ids_empty_when_no_work(self, tmp_path):
        ids = store.list_ids(repo_root=tmp_path)
        assert ids == []

    def test_list_ids_returns_sorted_ids(self, tmp_path):
        for wid in ["W-0003", "W-0001", "W-0002"]:
            store.save(_make_work(wid=wid), repo_root=tmp_path)

        ids = store.list_ids(repo_root=tmp_path)
        assert ids == ["W-0001", "W-0002", "W-0003"]

    def test_save_overwrites_existing(self, tmp_path):
        work = _make_work()
        store.save(work, repo_root=tmp_path)

        updated = work.transition_to(WorkStatus.SPECIFYING)
        store.save(updated, repo_root=tmp_path)

        loaded = store.load("W-0001", repo_root=tmp_path)
        assert loaded.status == WorkStatus.SPECIFYING

    def test_driftless_initialized_false_when_no_dir(self, tmp_path):
        assert store.driftless_initialized(repo_root=tmp_path) is False

    def test_driftless_initialized_true_after_save(self, tmp_path):
        store.save(_make_work(), repo_root=tmp_path)
        assert store.driftless_initialized(repo_root=tmp_path) is True

    def test_state_json_is_valid_json(self, tmp_path):
        import json

        work = _make_work(wid="W-0042", title="JSON test")
        store.save(work, repo_root=tmp_path)
        path = tmp_path / ".driftless" / "work" / "W-0042" / "state.json"
        data = json.loads(path.read_text())
        assert data["id"] == "W-0042"
        assert data["title"] == "JSON test"

    def test_multiple_works_can_coexist(self, tmp_path):
        for i in range(1, 6):
            store.save(
                _make_work(wid=f"W-{i:04d}", title=f"Work {i}"), repo_root=tmp_path
            )

        ids = store.list_ids(repo_root=tmp_path)
        assert len(ids) == 5
