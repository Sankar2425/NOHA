from __future__ import annotations

import re
from typing import Any

from runtime.brain.enums import PlanStatus, TaskStatus
from runtime.brain.models import ExecutionResult, Plan
from runtime.brain.task import Task
from runtime.tools.tool_registry import ToolRegistry


class Executor:
    """
    Executes a NOHA Plan through the ToolRegistry.

    Responsibilities
    ----------------
    - Execute tasks in dependency order.
    - Wait for dependencies to complete.
    - Resolve task-output references.
    - Pass task payloads to the correct tool.
    - Update Task runtime state.
    - Handle failures and retries.
    - Stop tasks whose dependencies failed.
    - Produce an ExecutionResult.

    The Executor does NOT:
    - understand natural language
    - classify intent
    - create plans
    - directly implement filesystem/browser/coding logic
    """

    TASK_OUTPUT_PATTERN = re.compile(
        r"\$TASK_(\d+)_OUTPUT"
    )

    def __init__(
        self,
        registry: ToolRegistry | None = None,
    ) -> None:
        """
        Initialize the Executor.

        If no registry is supplied, a default ToolRegistry
        is created.
        """

        self.registry = registry or ToolRegistry()

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    async def execute(
        self,
        plan: Plan,
    ) -> ExecutionResult:
        """
        Execute an entire plan.

        Tasks are executed according to their dependencies.
        """

        if not isinstance(plan, Plan):
            raise TypeError(
                "Executor expects a Plan."
            )

        if not plan.tasks:
            return ExecutionResult(
                success=True,
                message="Plan contains no tasks.",
            )

        plan.status = PlanStatus.RUNNING

        completed = 0
        failed = 0

        # ------------------------------------------------------
        # Execute tasks in plan order.
        #
        # The current Planner creates sequential dependencies,
        # so this naturally gives us deterministic execution.
        # ------------------------------------------------------

        for task in plan.tasks:

            if task.status == TaskStatus.SUCCESS:
                completed += 1
                continue

            # --------------------------------------------------
            # Check dependencies
            # --------------------------------------------------

            if not self._dependencies_satisfied(
                task,
                plan,
            ):

                task.status = TaskStatus.SKIPPED

                task.error = (
                    "Task dependencies were not completed "
                    "successfully."
                )

                failed += 1

                self._skip_dependents(
                    task,
                    plan,
                )

                continue

            # --------------------------------------------------
            # Execute task
            # --------------------------------------------------

            success = await self._execute_task(
                task,
                plan,
            )

            if success:
                completed += 1

            else:
                failed += 1

                self._skip_dependents(
                    task,
                    plan,
                )

                # Continue checking the remaining tasks.
                # Dependent tasks will be skipped.
                continue

        # ======================================================
        # FINAL PLAN STATUS
        # ======================================================

        if failed == 0:

            plan.status = PlanStatus.SUCCESS

            message = (
                f"Plan completed successfully. "
                f"{completed}/{len(plan.tasks)} tasks completed."
            )

            success = True

        elif completed > 0:

            plan.status = PlanStatus.PARTIAL_SUCCESS

            message = (
                f"Plan partially completed. "
                f"{completed}/{len(plan.tasks)} tasks completed."
            )

            success = False

        else:

            plan.status = PlanStatus.FAILED

            message = (
                "Plan execution failed. "
                "No tasks completed successfully."
            )

            success = False

        return ExecutionResult(
            success=success,
            completed_tasks=completed,
            failed_tasks=failed,
            message=message,
        )

    # ==========================================================
    # TASK EXECUTION
    # ==========================================================

    async def _execute_task(
        self,
        task: Task,
        plan: Plan,
    ) -> bool:
        """
        Execute one task through the ToolRegistry.
        """

        if not task.can_execute:
            return False

        # ------------------------------------------------------
        # Resolve task references
        # ------------------------------------------------------

        try:

            payload = self._resolve_payload(
                task.payload,
                plan,
            )

        except Exception as exc:

            task.fail(
                f"Failed to resolve task payload: {exc}"
            )

            return False

        # ------------------------------------------------------
        # Start task
        # ------------------------------------------------------

        task.start()

        try:

            result = await self.registry.execute(
                skill=task.skill,
                action=task.action.value,
                payload=payload,
            )

        except Exception as exc:

            task.fail(
                str(exc)
            )

            return False

        # ------------------------------------------------------
        # Validate tool result
        # ------------------------------------------------------

        if not isinstance(result, dict):

            task.fail(
                "Tool returned an invalid result."
            )

            return False

        status = result.get("status")

        # ------------------------------------------------------
        # SUCCESS
        # ------------------------------------------------------

        if status == "success":

            task.complete(
                result=result
            )

            return True

        # ------------------------------------------------------
        # FAILURE
        # ------------------------------------------------------

        message = result.get(
            "message",
            "Tool execution failed.",
        )

        task.fail(
            str(message)
        )

        return False

    # ==========================================================
    # DEPENDENCIES
    # ==========================================================

    def _dependencies_satisfied(
        self,
        task: Task,
        plan: Plan,
    ) -> bool:
        """
        Check whether all dependencies completed successfully.
        """

        if not task.dependencies:
            return True

        task_map = {
            item.id: item
            for item in plan.tasks
        }

        for dependency_id in task.dependencies:

            dependency = task_map.get(
                dependency_id
            )

            if dependency is None:
                return False

            if dependency.status != TaskStatus.SUCCESS:
                return False

        return True

    def _skip_dependents(
        self,
        failed_task: Task,
        plan: Plan,
    ) -> None:
        """
        Skip tasks that directly or indirectly depend on
        a failed task.
        """

        changed = True

        while changed:

            changed = False

            for task in plan.tasks:

                if task.status != TaskStatus.PENDING:
                    continue

                if failed_task.id in task.dependencies:

                    task.status = TaskStatus.SKIPPED

                    task.error = (
                        f"Dependency failed: "
                        f"{failed_task.id}"
                    )

                    changed = True

                    failed_task = task

    # ==========================================================
    # OUTPUT RESOLUTION
    # ==========================================================

    def _resolve_payload(
        self,
        payload: dict[str, Any],
        plan: Plan,
    ) -> dict[str, Any]:
        """
        Resolve $TASK_N_OUTPUT references inside a payload.

        Example:

            {
                "content": "$TASK_3_OUTPUT"
            }

        becomes the result of Task 3.

        Nested dictionaries and lists are supported.
        """

        return self._resolve_value(
            payload,
            plan,
        )

    def _resolve_value(
        self,
        value: Any,
        plan: Plan,
    ) -> Any:
        """
        Recursively resolve task-output references.
        """

        if isinstance(value, dict):

            return {
                key: self._resolve_value(
                    item,
                    plan,
                )
                for key, item in value.items()
            }

        if isinstance(value, list):

            return [
                self._resolve_value(
                    item,
                    plan,
                )
                for item in value
            ]

        if isinstance(value, str):

            match = self.TASK_OUTPUT_PATTERN.fullmatch(
                value.strip()
            )

            if match:

                task_number = int(
                    match.group(1)
                )

                return self._get_task_output(
                    task_number,
                    plan,
                )

            return value

        return value

    def _get_task_output(
        self,
        task_number: int,
        plan: Plan,
    ) -> Any:
        """
        Retrieve the result of Task N.

        Task numbering is based on the Planner's
        human-readable 1-based ordering.
        """

        index = task_number - 1

        if index < 0 or index >= len(plan.tasks):

            raise IndexError(
                f"Task reference {task_number} "
                f"does not exist."
            )

        task = plan.tasks[index]

        if task.status != TaskStatus.SUCCESS:

            raise RuntimeError(
                f"Task {task_number} has not completed successfully."
            )

        return task.result

    # ==========================================================
    # DEBUGGING
    # ==========================================================

    def describe_execution(
        self,
        plan: Plan,
    ) -> str:
        """
        Return a readable execution summary.
        """

        lines = [
            "=" * 50,
            "NOHA EXECUTION",
            "=" * 50,
            "",
            f"Goal: {plan.goal}",
            f"Status: {plan.status.value}",
            "",
        ]

        for index, task in enumerate(
            plan.tasks,
            start=1,
        ):

            lines.append(
                f"Task {index}: {task.name}"
            )

            lines.append(
                f"  Skill : {task.skill.value}"
            )

            lines.append(
                f"  Action: {task.action.value}"
            )

            lines.append(
                f"  Status: {task.status.value}"
            )

            if task.result is not None:

                lines.append(
                    f"  Result: {task.result}"
                )

            if task.error:

                lines.append(
                    f"  Error : {task.error}"
                )

            lines.append("")

        return "\n".join(lines)