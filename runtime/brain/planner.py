from __future__ import annotations

from typing import Any

from runtime.brain.enums import PlanStatus, TaskAction, TaskStatus
from runtime.brain.models import IntentResult, Plan
from runtime.brain.task import Task


class Planner:
    """
    Converts an IntentResult into an executable Plan.

    Responsibilities
    ----------------
    - Convert IntentTask objects into executable Task objects.
    - Preserve task ordering.
    - Establish dependencies between ordered tasks.
    - Preserve task parameters/payloads.
    - Preserve task-output references such as $TASK_3_OUTPUT.
    - Validate the resulting plan.
    - Never execute tasks.
    """

    def create_plan(self, intent_result: IntentResult) -> Plan:
        """
        Build an executable Plan from an IntentResult.
        """

        if not isinstance(intent_result, IntentResult):
            raise TypeError(
                "Planner expects an IntentResult."
            )

        if not intent_result.goal.strip():
            raise ValueError(
                "IntentResult goal cannot be empty."
            )

        if not intent_result.tasks:
            raise ValueError(
                "Cannot create a plan without tasks."
            )

        tasks: list[Task] = []

        for index, intent_task in enumerate(
            intent_result.tasks,
            start=1,
        ):
            task = self._build_task(
                intent_task=intent_task,
                index=index,
            )

            tasks.append(task)

        self._enrich_code_generation_tasks(tasks)

        self._assign_dependencies(tasks)

        plan = Plan(
            goal=intent_result.goal,
            intent=intent_result.intent,
            tasks=tasks,
            status=PlanStatus.CREATED,
            summary=intent_result.reasoning,
            metadata={
                "source": "intent_classifier",
                "confidence": intent_result.confidence,
                "command": intent_result.command,
            },
        )

        self._validate_plan(plan)

        return plan

    # ==========================================================
    # TASK CREATION
    # ==========================================================

    def _build_task(
        self,
        intent_task: Any,
        index: int,
    ) -> Task:
        """
        Convert one IntentTask into an executable Task.
        """

        name = self._build_task_name(
            intent_task.action.value,
            index,
        )

        description = self._build_task_description(
            intent_task,
        )

        payload = dict(
            intent_task.parameters
        )

        task = Task(
            name=name,
            description=description,
            skill=intent_task.skill,
            action=intent_task.action,
            payload=payload,
            priority=0,
            status=TaskStatus.PENDING,
            metadata={
                "planner_index": index,
                "source": "intent_classifier",
            },
        )

        return task

    def _enrich_code_generation_tasks(
        self,
        tasks: list[Task],
    ) -> None:
        """Connect generated code to its later filesystem write task.

        Intent classification describes tasks independently. When a generated
        code output is written to a file later in the same plan, the Planner
        adds the destination filename required by CodeGenerator and makes the
        output field explicit for the Executor.
        """

        for index, code_task in enumerate(tasks, start=1):

            if code_task.action != TaskAction.GENERATE_CODE:
                continue

            output_reference = f"$TASK_{index}_OUTPUT"

            for write_task in tasks[index:]:

                if (
                    write_task.action != TaskAction.WRITE_FILE
                    or write_task.payload.get("content")
                    != output_reference
                ):
                    continue

                path = write_task.payload.get("path")

                if isinstance(path, str) and path.strip():
                    code_task.payload.setdefault(
                        "file_name",
                        path,
                    )

                write_task.payload["content"] = (
                    f"{output_reference}.code"
                )

                break

    # ==========================================================
    # TASK NAMING
    # ==========================================================

    def _build_task_name(
        self,
        action: str,
        index: int,
    ) -> str:
        """
        Generate a readable task name.
        """

        readable = action.replace(
            "_",
            " ",
        ).title()

        return f"Task {index}: {readable}"

    def _build_task_description(
        self,
        intent_task: Any,
    ) -> str:
        """
        Generate a useful description for the executor/debugging.
        """

        action = intent_task.action.value

        skill = intent_task.skill.value

        return (
            f"Execute '{action}' using "
            f"the '{skill}' skill."
        )

    # ==========================================================
    # DEPENDENCIES
    # ==========================================================

    def _assign_dependencies(
        self,
        tasks: list[Task],
    ) -> None:
        """
        Establish execution dependencies.

        The first task has no dependency.

        Every later task depends on the previous task.

        This preserves the ordered execution semantics produced
        by the IntentClassifier.

        Example:

            Task 1
              ↓
            Task 2
              ↓
            Task 3
              ↓
            Task 4
        """

        for index, task in enumerate(tasks):

            if index == 0:
                task.dependencies = []
                continue

            previous_task = tasks[index - 1]

            task.dependencies = [
                previous_task.id
            ]

    # ==========================================================
    # PLAN VALIDATION
    # ==========================================================

    def _validate_plan(
        self,
        plan: Plan,
    ) -> None:
        """
        Validate the generated execution plan.
        """

        if not plan.goal.strip():
            raise ValueError(
                "Plan goal cannot be empty."
            )

        if not plan.tasks:
            raise ValueError(
                "Plan must contain at least one task."
            )

        task_ids = set()

        for task in plan.tasks:

            # ----------------------------------------------
            # Unique task IDs
            # ----------------------------------------------

            if task.id in task_ids:
                raise ValueError(
                    f"Duplicate task ID detected: {task.id}"
                )

            task_ids.add(task.id)

            # ----------------------------------------------
            # Valid task
            # ----------------------------------------------

            if not task.name.strip():
                raise ValueError(
                    "Plan contains a task without a name."
                )

            # ----------------------------------------------
            # Dependency validation
            # ----------------------------------------------

            for dependency in task.dependencies:

                if dependency not in task_ids:
                    raise ValueError(
                        "Task dependency refers to a task "
                        "that has not been created yet."
                    )

    # ==========================================================
    # EXECUTION READINESS
    # ==========================================================

    def mark_ready_tasks(
        self,
        plan: Plan,
    ) -> None:
        """
        Mark tasks as READY when all dependencies have
        completed successfully.

        This does not execute anything.
        """

        completed_ids = {
            task.id
            for task in plan.tasks
            if task.status == TaskStatus.SUCCESS
        }

        for task in plan.tasks:

            if task.status != TaskStatus.PENDING:
                continue

            dependencies_ready = all(
                dependency in completed_ids
                for dependency in task.dependencies
            )

            if dependencies_ready:
                task.status = TaskStatus.READY

    # ==========================================================
    # PLAN SUMMARY
    # ==========================================================

    def describe_plan(
        self,
        plan: Plan,
    ) -> str:
        """
        Return a human-readable representation of the plan.
        """

        lines = [
            f"Goal: {plan.goal}",
            f"Intent: {plan.intent.value}",
            f"Tasks: {len(plan.tasks)}",
            "",
        ]

        for index, task in enumerate(
            plan.tasks,
            start=1,
        ):

            lines.append(
                f"{index}. {task.name}"
            )

            lines.append(
                f"   Skill: {task.skill.value}"
            )

            lines.append(
                f"   Action: {task.action.value}"
            )

            lines.append(
                f"   Status: {task.status.value}"
            )

            if task.dependencies:
                lines.append(
                    "   Dependencies: "
                    + ", ".join(task.dependencies)
                )

            if task.payload:
                lines.append(
                    f"   Payload: {task.payload}"
                )

            lines.append("")

        return "\n".join(lines)
