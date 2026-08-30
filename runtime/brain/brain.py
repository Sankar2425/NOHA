from __future__ import annotations

from runtime.brain.context import BrainContext
from runtime.brain.enums import ExecutionStatus
from runtime.brain.executor import Executor
from runtime.brain.intent_classifier import IntentClassifier
from runtime.brain.models import (
    ExecutionResult,
    ReflectionResult,
)
from runtime.brain.planner import Planner
from runtime.brain.reflection import Reflection
from runtime.brain.state import BrainState


class Brain:
    """
    Central orchestration engine for NOHA.

    Pipeline:

        User Command
             │
             ▼
        Context Update
             │
             ▼
      Intent Classification
             │
             ▼
          Planning
             │
             ▼
          Execution
             │
             ▼
          Reflection
             │
             ▼
       ReflectionResult
    """

    def __init__(
        self,
        context: BrainContext,
        state: BrainState,
        classifier: IntentClassifier,
        planner: Planner,
        executor: Executor,
        reflection: Reflection,
    ) -> None:

        self.context = context
        self.state = state

        self.classifier = classifier
        self.planner = planner
        self.executor = executor
        self.reflection = reflection

    async def process(
        self,
        command: str,
    ) -> ReflectionResult:
        """
        Process a single user command.
        """

        command = command.strip()

        if not command:
            raise ValueError("Command cannot be empty.")

        self.state.execution_status = ExecutionStatus.RUNNING

        try:

            # -------------------------------------------------
            # Context
            # -------------------------------------------------

            self.context.last_user_command = command
            self.state.current_goal = command

            # -------------------------------------------------
            # Intent Classification
            # -------------------------------------------------

            intent = await self.classifier.classify(command)

            self.state.current_intent = intent

            # -------------------------------------------------
            # Planning
            # -------------------------------------------------

            plan = self.planner.create_plan(intent)

            self.state.current_plan = plan

            # -------------------------------------------------
            # Execution
            # -------------------------------------------------

            execution: ExecutionResult = (
                await self.executor.execute(plan)
            )

            self.state.last_execution = execution

            # -------------------------------------------------
            # Reflection
            # -------------------------------------------------

            reflection: ReflectionResult = (
                await self.reflection.reflect(execution)
            )

            reflection.execution = execution

            self.state.last_reflection = reflection

            return reflection

        except Exception as exc:

            self.state.last_error = str(exc)

            raise

        finally:

            self.state.execution_status = ExecutionStatus.IDLE
