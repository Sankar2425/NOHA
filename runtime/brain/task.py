from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from runtime.brain.enums import (
    SkillType,
    TaskAction,
    TaskStatus,
)


@dataclass(slots=True)
class Task:
    """
    Represents a single executable task inside NOHA.

    A Task is created by the Planner and later executed
    by the Executor.

    Example:

        Create project folder
        Generate Python code
        Write generated code to file
        Run application
    """

    # ==========================================================
    # IDENTITY
    # ==========================================================

    id: str = field(
        default_factory=lambda: str(uuid4())
    )

    # ==========================================================
    # DESCRIPTION
    # ==========================================================

    name: str = ""

    description: str = ""

    # ==========================================================
    # EXECUTION
    # ==========================================================

    skill: SkillType = SkillType.FILESYSTEM

    action: TaskAction = TaskAction.UNKNOWN

    # ==========================================================
    # SCHEDULING
    # ==========================================================

    priority: int = 0

    dependencies: list[str] = field(
        default_factory=list
    )

    # ==========================================================
    # INPUT
    # ==========================================================

    payload: dict[str, Any] = field(
        default_factory=dict
    )

    # ==========================================================
    # EXECUTION METADATA
    # ==========================================================

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # ==========================================================
    # RUNTIME STATE
    # ==========================================================

    status: TaskStatus = TaskStatus.PENDING

    result: Any = None

    error: str | None = None

    retries: int = 0

    max_retries: int = 3

    # ==========================================================
    # TIMING
    # ==========================================================

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    started_at: datetime | None = None

    finished_at: datetime | None = None

    # ==========================================================
    # VALIDATION
    # ==========================================================

    def __post_init__(self) -> None:

        if not isinstance(self.name, str):
            raise TypeError(
                "Task name must be a string."
            )

        if not self.name.strip():
            raise ValueError(
                "Task name cannot be empty."
            )

        if not isinstance(self.skill, SkillType):
            raise TypeError(
                "Task skill must be a SkillType."
            )

        if not isinstance(self.action, TaskAction):
            raise TypeError(
                "Task action must be a TaskAction."
            )

        if not isinstance(self.payload, dict):
            raise TypeError(
                "Task payload must be a dictionary."
            )

        if not isinstance(self.dependencies, list):
            raise TypeError(
                "Task dependencies must be a list."
            )

        if self.priority < 0:
            raise ValueError(
                "Task priority cannot be negative."
            )

        if self.max_retries < 0:
            raise ValueError(
                "max_retries cannot be negative."
            )

    # ==========================================================
    # PROPERTIES
    # ==========================================================

    @property
    def duration(self) -> timedelta | None:
        """
        Return execution duration if the task has finished.
        """

        if self.started_at and self.finished_at:
            return self.finished_at - self.started_at

        return None

    @property
    def can_execute(self) -> bool:
        """
        Determine whether the task is currently executable.
        """

        return self.status in (
            TaskStatus.PENDING,
            TaskStatus.READY,
        )

    @property
    def can_retry(self) -> bool:
        """
        Determine whether another execution attempt is allowed.
        """

        return self.retries < self.max_retries

    @property
    def is_finished(self) -> bool:
        """
        Determine whether execution has reached a terminal state.
        """

        return self.status in (
            TaskStatus.SUCCESS,
            TaskStatus.FAILED,
            TaskStatus.SKIPPED,
        )

    # ==========================================================
    # STATE MANAGEMENT
    # ==========================================================

    def start(self) -> None:
        """
        Mark the task as running.
        """

        if not self.can_execute:
            raise RuntimeError(
                f"Task cannot start from status "
                f"'{self.status.value}'."
            )

        self.status = TaskStatus.RUNNING

        self.started_at = datetime.utcnow()

        self.finished_at = None

    def complete(self, result: Any = None) -> None:
        """
        Mark the task as successfully completed.
        """

        self.status = TaskStatus.SUCCESS

        self.result = result

        self.error = None

        self.finished_at = datetime.utcnow()

    def fail(self, error: str) -> None:
        """
        Mark the task as failed.
        """

        if not isinstance(error, str):
            error = str(error)

        self.status = TaskStatus.FAILED

        self.error = error

        self.retries += 1

        self.finished_at = datetime.utcnow()

    def reset(self) -> None:
        """
        Reset the task for another execution attempt.
        """

        self.status = TaskStatus.PENDING

        self.result = None

        self.error = None

        self.started_at = None

        self.finished_at = None