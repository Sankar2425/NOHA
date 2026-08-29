from __future__ import annotations

from runtime.brain.enums import IntentType, SkillType, TaskAction
from runtime.brain.models import IntentResult, IntentTask
from runtime.brain.planner import Planner


def main() -> None:

    intent_result = IntentResult(
        goal="Create a Python calculator application",
        intent=IntentType.FILESYSTEM,
        tasks=[
            IntentTask(
                skill=SkillType.FILESYSTEM,
                action=TaskAction.CREATE_FOLDER,
                parameters={
                    "path": "test"
                },
            ),
            IntentTask(
                skill=SkillType.FILESYSTEM,
                action=TaskAction.CREATE_FILE,
                parameters={
                    "path": "test/app.py"
                },
            ),
            IntentTask(
                skill=SkillType.CODING,
                action=TaskAction.GENERATE_CODE,
                parameters={
                    "language": "python",
                    "prompt": (
                        "Create a Python calculator program."
                    ),
                },
            ),
            IntentTask(
                skill=SkillType.FILESYSTEM,
                action=TaskAction.WRITE_FILE,
                parameters={
                    "path": "test/app.py",
                    "content": "$TASK_3_OUTPUT",
                },
            ),
        ],
        confidence=0.98,
        reasoning=(
            "The folder and file must exist before "
            "generated code can be written."
        ),
        command=(
            "Create a folder called test, create app.py "
            "inside it, generate a Python calculator, "
            "and write it to the file."
        ),
    )

    planner = Planner()

    plan = planner.create_plan(
        intent_result
    )

    print()
    print("=" * 50)
    print("NOHA PLANNER TEST")
    print("=" * 50)

    print()
    print(planner.describe_plan(plan))

    print("=" * 50)
    print("PLANNER SUCCESS")
    print("=" * 50)


if __name__ == "__main__":
    main()