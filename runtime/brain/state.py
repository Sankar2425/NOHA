from __future__ import annotations

from dataclasses import dataclass

from runtime.brain.enums import (
    ExecutionStatus,
    SkillType,
)
from runtime.brain.models import (
    ExecutionResult,
    IntentResult,
    Plan,
    ReflectionResult,
)
from runtime.brain.task import Task


@dataclass(slots=True)
class BrainState:
    """
    Represents the current runtime state of the Brain.

    This object stores only transient execution state.
    It does not contain business logic.
    """

    # ---------------------------------------------------------
    # Current request
    # ---------------------------------------------------------

    current_goal: str = ""

    current_intent: IntentResult | None = None

    current_plan: Plan | None = None

    current_task: Task | None = None

    active_skill: SkillType | None = None

    # ---------------------------------------------------------
    # Execution tracking
    # ---------------------------------------------------------

    current_task_index: int = 0

    retry_count: int = 0

    execution_status: ExecutionStatus = ExecutionStatus.IDLE

    # ---------------------------------------------------------
    # Latest results
    # ---------------------------------------------------------

    last_execution: ExecutionResult | None = None

    last_reflection: ReflectionResult | None = None

    last_error: str | None = None

    # ---------------------------------------------------------
    # Reset
    # ---------------------------------------------------------

    def reset(self) -> None:
        """Reset runtime state."""

        self.current_goal = ""

        self.current_intent = None

        self.current_plan = None

        self.current_task = None

        self.active_skill = None

        self.current_task_index = 0

        self.retry_count = 0

        self.execution_status = ExecutionStatus.IDLE

        self.last_execution = None

        self.last_reflection = None

        self.last_error = None