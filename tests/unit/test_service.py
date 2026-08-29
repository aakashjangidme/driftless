"""Unit tests for Work service following AAA pattern."""

import time

from driftless.state import store
from driftless.work import service as work_service
from driftless.work.models import Work, WorkStatus, WorkType


class TestCreateWork:
    def test_create_work_success_in_git_repo(self, tmp_path, mocker):
        # Arrange
        git_mock = mocker.patch("driftless.work.service.GitAdapter").return_value
        git_mock.is_repo.return_value = True
        git_mock.branch.return_value = "feature/oauth"
        git_mock.root.return_value = tmp_path

        # Act
        work = work_service.create_work(
            "Add OAuth login", work_type=WorkType.feature, repo_root=tmp_path
        )

        # Assert
        assert work.id == "W-0001"
        assert work.title == "Add OAuth login"
        assert work.type == WorkType.feature
        assert work.status == WorkStatus.CREATED
        assert work.branch == "feature/oauth"
        assert work.repository == str(tmp_path)
        assert store.load("W-0001", repo_root=tmp_path).title == "Add OAuth login"

    def test_create_work_handles_git_adapter_exceptions(self, tmp_path, mocker):
        # Arrange
        git_mock = mocker.patch("driftless.work.service.GitAdapter").return_value
        git_mock.is_repo.return_value = True
        git_mock.branch.side_effect = Exception("Git branch error")
        git_mock.root.side_effect = Exception("Git root error")

        # Act
        work = work_service.create_work("Resilient Work", repo_root=tmp_path)

        # Assert
        assert work.branch is None
        assert work.repository is None

    def test_create_work_outside_git_repo(self, tmp_path, mocker):
        # Arrange
        git_mock = mocker.patch("driftless.work.service.GitAdapter").return_value
        git_mock.is_repo.return_value = False

        # Act
        work = work_service.create_work("No Git Work", repo_root=tmp_path)

        # Assert
        assert work.branch is None
        assert work.repository is None

    def test_sequential_id_generation(self, tmp_path, mocker):
        # Arrange
        git_mock = mocker.patch("driftless.work.service.GitAdapter").return_value
        git_mock.is_repo.return_value = False

        # Act
        w1 = work_service.create_work("First", repo_root=tmp_path)
        w2 = work_service.create_work("Second", repo_root=tmp_path)
        w3 = work_service.create_work("Third", repo_root=tmp_path)

        # Assert
        assert w1.id == "W-0001"
        assert w2.id == "W-0002"
        assert w3.id == "W-0003"


class TestListWorks:
    def test_list_works_returns_empty_list_when_no_works(self, tmp_path):
        # Arrange & Act
        works = work_service.list_works(repo_root=tmp_path)

        # Assert
        assert works == []

    def test_list_works_returns_all_persisted_works(self, tmp_path, mocker):
        # Arrange
        git_mock = mocker.patch("driftless.work.service.GitAdapter").return_value
        git_mock.is_repo.return_value = False
        work_service.create_work("A", repo_root=tmp_path)
        work_service.create_work("B", repo_root=tmp_path)

        # Act
        works = work_service.list_works(repo_root=tmp_path)

        # Assert
        assert len(works) == 2
        assert works[0].id == "W-0001"
        assert works[1].id == "W-0002"

    def test_list_works_handles_invalid_state_files(self, tmp_path, mocker):
        # Arrange
        mocker.patch(
            "driftless.work.service.store.list_ids", return_value=["W-0001", "W-BAD"]
        )
        mocker.patch(
            "driftless.work.service.store.load",
            side_effect=[Work(id="W-0001", title="Valid"), ValueError("Corrupt")],
        )

        # Act
        works = work_service.list_works(repo_root=tmp_path)

        # Assert
        assert len(works) == 1
        assert works[0].id == "W-0001"


class TestLoadWork:
    def test_load_work_returns_work_by_id(self, tmp_path, mocker):
        # Arrange
        git_mock = mocker.patch("driftless.work.service.GitAdapter").return_value
        git_mock.is_repo.return_value = False
        created = work_service.create_work("Target Work", repo_root=tmp_path)

        # Act
        loaded = work_service.load_work(created.id, repo_root=tmp_path)

        # Assert
        assert loaded.id == created.id
        assert loaded.title == "Target Work"


class TestActiveWork:
    def test_active_work_returns_none_when_empty(self, tmp_path):
        # Arrange & Act
        active = work_service.active_work(repo_root=tmp_path)

        # Assert
        assert active is None

    def test_active_work_returns_most_recently_updated_non_done(self, tmp_path, mocker):
        # Arrange
        git_mock = mocker.patch("driftless.work.service.GitAdapter").return_value
        git_mock.is_repo.return_value = False
        w1 = work_service.create_work("Older Work", repo_root=tmp_path)
        time.sleep(0.01)
        w2 = work_service.create_work("Newer Work", repo_root=tmp_path)

        # Act
        active = work_service.active_work(repo_root=tmp_path)

        # Assert
        assert active is not None
        assert active.id == w2.id

    def test_active_work_ignores_done_works(self, tmp_path):
        # Arrange
        done_work = Work(id="W-0001", title="Done Task", status=WorkStatus.DONE)
        store.save(done_work, repo_root=tmp_path)

        # Act
        active = work_service.active_work(repo_root=tmp_path)

        # Assert
        assert active is None


class TestTransitionAndLink:
    def test_transition_updates_and_persists_status(self, tmp_path):
        # Arrange
        work = Work(id="W-0001", title="Test", status=WorkStatus.CREATED)
        store.save(work, repo_root=tmp_path)

        # Act
        updated = work_service.transition(
            work, WorkStatus.SPECIFYING, repo_root=tmp_path
        )

        # Assert
        assert updated.status == WorkStatus.SPECIFYING
        assert store.load("W-0001", repo_root=tmp_path).status == WorkStatus.SPECIFYING

    def test_link_openspec_change_updates_and_persists(self, tmp_path):
        # Arrange
        work = Work(id="W-0001", title="Test", status=WorkStatus.CREATED)
        store.save(work, repo_root=tmp_path)

        # Act
        updated = work_service.link_openspec_change(
            work, "add-oauth", repo_root=tmp_path
        )

        # Assert
        assert updated.openspec_change == "add-oauth"
        assert store.load("W-0001", repo_root=tmp_path).openspec_change == "add-oauth"
