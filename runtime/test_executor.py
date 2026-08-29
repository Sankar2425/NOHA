from __future__ import annotations

import asyncio

from runtime.brain.enums import IntentType, SkillType, TaskAction
from runtime.brain.executor import Executor
from runtime.brain.models import IntentResult, IntentTask
from runtime.brain.planner import Planner


async def main() -> None:

    print("=" * 50)
    print("NOHA EXECUTOR TEST")
    print("=" * 50)

    # ======================================================
    # INTENT
    # ======================================================

    intent_result = IntentResult(
        goal="Create a test file and write generated code into it.",
        intent=IntentType.FILESYSTEM,
        tasks=[
            IntentTask(
                skill=SkillType.FILESYSTEM,
                action=TaskAction.CREATE_FOLDER,
                parameters={
                    "path": "executor_test",
                },
            ),
            IntentTask(
                skill=SkillType.FILESYSTEM,
                action=TaskAction.CREATE_FILE,
                parameters={
                    "path": "executor_test/test.py",
                },
            ),
            IntentTask(
                skill=SkillType.CODING,
                action=TaskAction.GENERATE_CODE,
                parameters={
                    "language": "python",
                    "prompt": (
                        "Create a Python function called "
                        "hello that returns the string 'Hello NOHA'."
                    ),
                },
            ),
            IntentTask(
                skill=SkillType.FILESYSTEM,
                action=TaskAction.WRITE_FILE,
                parameters={
                    "path": "executor_test/test.py",
                    "content": "$TASK_3_OUTPUT",
                },
            ),
        ],
        confidence=0.99,
        reasoning=(
            "The folder and file must exist before "
            "generated code can be written."
        ),
        command=(
            "Create a test file and write generated "
            "code into it."
        ),
    )

    # ======================================================
    # PLANNER
    # ======================================================

    planner = Planner()

    plan = planner.create_plan(
        intent_result
    )

    print("\nPLAN CREATED")
    print("-" * 50)

    print(
        planner.describe_plan(plan)
    )

    # ======================================================
    # EXECUTOR
    # ======================================================

    executor = Executor()

    print("\nEXECUTING PLAN...")
    print("-" * 50)

    result = await executor.execute(
        plan
    )

    # ======================================================
    # RESULT
    # ======================================================

    print(
        executor.describe_execution(plan)
    )

    print("-" * 50)

    print(
        f"Success          : {result.success}"
    )

    print(
        f"Completed tasks  : {result.completed_tasks}"
    )

    print(
        f"Failed tasks     : {result.failed_tasks}"
    )

    print(
        f"Message          : {result.message}"
    )

    # ======================================================
    # VALIDATION
    # ======================================================

    if not result.success:
        raise RuntimeError(
            "Executor test failed."
        )

    for task in plan.tasks:

        if task.status.value != "success":

            raise RuntimeError(
                f"Task failed: {task.name}"
            )

    print("\n" + "=" * 50)
    print("EXECUTOR SUCCESS")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())