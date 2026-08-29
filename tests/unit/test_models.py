"""Unit tests for Work domain models following AAA pattern."""

from datetime import datetime

import pytest

from driftless.work.models import (
    ALLOWED_TRANSITIONS,
    Work,
    WorkStatus,
    WorkType,
)


class TestWorkType:
    def test_all_work_types_are_string_enums(self):
        # Arrange
        expected_types = {
            "feature",
            "bug",
            "refactor",
            "migration",
            "incident",
            "maintenance",
        }

        # Act
        actual_types = {t.value for t in WorkType}

        # Assert
        assert actual_types == expected_types
        assert WorkType.feature == "feature"


class TestWorkStatus:
    def test_all_work_statuses_are_string_enums(self):
        # Arrange
        expected_statuses = {
            "CREATED",
            "SPECIFYING",
            "PLANNING",
            "IMPLEMENTING",
            "VERIFYING",
            "REVIEW",
            "DELIVERY",
            "DONE",
        }

        # Act
        actual_statuses = {s.value for s in WorkStatus}

        # Assert
        assert actual_statuses == expected_statuses
        assert WorkStatus.CREATED == "CREATED"


class TestAllowedTransitions:
    def test_created_allowed_transitions(self):
        # Arrange
        status = WorkStatus.CREATED

        # Act
        allowed = ALLOWED_TRANSITIONS[status]

        # Assert
        assert WorkStatus.SPECIFYING in allowed
        assert WorkStatus.PLANNING in allowed
        assert WorkStatus.IMPLEMENTING in allowed

    def test_done_has_no_allowed_transitions(self):
        # Arrange
        status = WorkStatus.DONE

        # Act
        allowed = ALLOWED_TRANSITIONS[status]

        # Assert
        assert allowed == []


class TestWorkModel:
    def test_work_default_initialization(self):
        # Arrange & Act
        work = Work(id="W-0001", title="Test Work")

        # Assert
        assert work.id == "W-0001"
        assert work.title == "Test Work"
        assert work.type == WorkType.feature
        assert work.status == WorkStatus.CREATED
        assert work.repository is None
        assert work.branch is None
        assert work.openspec_change is None
        assert work.references == []
        assert isinstance(work.created_at, datetime)
        assert isinstance(work.updated_at, datetime)

    def test_can_transition_to_valid_target(self):
        # Arrange
        work = Work(id="W-0001", title="Test", status=WorkStatus.CREATED)

        # Act
        result = work.can_transition_to(WorkStatus.SPECIFYING)

        # Assert
        assert result is True

    def test_can_transition_to_invalid_target(self):
        # Arrange
        work = Work(id="W-0001", title="Test", status=WorkStatus.CREATED)

        # Act
        result = work.can_transition_to(WorkStatus.DONE)

        # Assert
        assert result is False

    def test_transition_to_valid_status_returns_new_instance(self):
        # Arrange
        initial_work = Work(id="W-0001", title="Test", status=WorkStatus.CREATED)

        # Act
        updated_work = initial_work.transition_to(WorkStatus.SPECIFYING)

        # Assert
        assert updated_work.status == WorkStatus.SPECIFYING
        assert updated_work.id == initial_work.id
        assert initial_work.status == WorkStatus.CREATED  # Immutable update
        assert updated_work.updated_at >= initial_work.updated_at

    def test_transition_to_invalid_status_raises_value_error(self):
        # Arrange
        work = Work(id="W-0001", title="Test", status=WorkStatus.DONE)

        # Act & Assert
        with pytest.raises(
            ValueError, match="Cannot transition Work W-0001 from DONE to CREATED"
        ):
            work.transition_to(WorkStatus.CREATED)

    def test_is_active_returns_true_for_non_done(self):
        # Arrange
        work = Work(id="W-0001", title="Test", status=WorkStatus.IMPLEMENTING)

        # Act
        active = work.is_active()

        # Assert
        assert active is True

    def test_is_active_returns_false_for_done(self):
        # Arrange
        work = Work(id="W-0001", title="Test", status=WorkStatus.DONE)

        # Act
        active = work.is_active()

        # Assert
        assert active is False

    def test_model_json_serialization_round_trip(self):
        # Arrange
        original = Work(
            id="W-0042",
            title="OAuth Flow",
            type=WorkType.feature,
            status=WorkStatus.PLANNING,
            openspec_change="add-oauth",
            branch="feature/oauth",
            references=["JIRA-101"],
        )

        # Act
        json_str = original.model_dump_json()
        restored = Work.model_validate_json(json_str)

        # Assert
        assert restored == original
