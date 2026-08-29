"""Work domain models — WorkType, WorkStatus, Work."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field


class WorkType(StrEnum):
    """Type of engineering work."""

    feature = "feature"
    bug = "bug"
    refactor = "refactor"
    migration = "migration"
    incident = "incident"
    maintenance = "maintenance"


class WorkStatus(StrEnum):
    """Outer-loop lifecycle stages for a Work."""

    CREATED = "CREATED"
    SPECIFYING = "SPECIFYING"
    PLANNING = "PLANNING"
    IMPLEMENTING = "IMPLEMENTING"
    VERIFYING = "VERIFYING"
    REVIEW = "REVIEW"
    DELIVERY = "DELIVERY"
    DONE = "DONE"


# Explicit allowed transitions to keep the state machine testable and auditable.
ALLOWED_TRANSITIONS: dict[WorkStatus, list[WorkStatus]] = {
    WorkStatus.CREATED: [
        WorkStatus.SPECIFYING,
        WorkStatus.PLANNING,
        WorkStatus.IMPLEMENTING,
    ],
    WorkStatus.SPECIFYING: [
        WorkStatus.PLANNING,
        WorkStatus.IMPLEMENTING,
        WorkStatus.VERIFYING,
        WorkStatus.REVIEW,
    ],
    WorkStatus.PLANNING: [
        WorkStatus.IMPLEMENTING,
        WorkStatus.VERIFYING,
        WorkStatus.REVIEW,
    ],
    WorkStatus.IMPLEMENTING: [WorkStatus.VERIFYING, WorkStatus.REVIEW],
    WorkStatus.VERIFYING: [WorkStatus.REVIEW, WorkStatus.IMPLEMENTING],
    WorkStatus.REVIEW: [WorkStatus.DELIVERY, WorkStatus.DONE, WorkStatus.IMPLEMENTING],
    WorkStatus.DELIVERY: [WorkStatus.DONE],
    WorkStatus.DONE: [],
}


def _now() -> datetime:
    return datetime.now(tz=UTC)


class Work(BaseModel):
    """Represents a unit of engineering work in the Driftless outer loop."""

    model_config = ConfigDict(use_enum_values=False)

    id: str
    title: str
    type: WorkType = WorkType.feature
    status: WorkStatus = WorkStatus.CREATED
    repository: str | None = None
    branch: str | None = None
    openspec_change: str | None = None
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    references: list[str] = Field(default_factory=list)

    def can_transition_to(self, new_status: WorkStatus) -> bool:
        """Return True if transitioning to new_status is allowed from current status."""
        return new_status in ALLOWED_TRANSITIONS.get(self.status, [])

    def transition_to(self, new_status: WorkStatus) -> Work:
        """Return a new Work with updated status and updated_at.

        Raises ValueError if the transition is not allowed.
        """
        if not self.can_transition_to(new_status):
            allowed = [s.value for s in ALLOWED_TRANSITIONS.get(self.status, [])]
            raise ValueError(
                f"Cannot transition Work {self.id} from {self.status.value} to "
                f"{new_status.value}. Allowed transitions: {allowed or ['none']}"
            )
        return self.model_copy(update={"status": new_status, "updated_at": _now()})

    def is_active(self) -> bool:
        """Return True if this Work is not yet DONE."""
        return self.status != WorkStatus.DONE
