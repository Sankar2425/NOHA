from __future__ import annotations

from runtime.brain.task import Task
from runtime.skills.base import BaseSkill


class CodingSkill(BaseSkill):
    """
    Skill responsible for code generation workflows.

    Workflow:
        1. Generate source code
        2. Optionally save it
        3. Optionally execute it
    """

    name = "coding"
    description = "Generates and executes source code."

    CODE_TOOL = "code_tool"
    FILE_TOOL = "file_tool"
    RUN_TOOL = "run_code_tool"

    async def execute(self, task: Task) -> dict:

        payload = task.payload.copy()

        prompt = payload.get("prompt")
        path = payload.get("path")
        auto_run = payload.get("run", False)

        code_tool = self.get_tool(self.CODE_TOOL)

        # --------------------------------------------------
        # Step 1 : Generate code
        # --------------------------------------------------

        generated = await code_tool.execute(
            {
                "prompt": prompt
            }
        )

        if generated["status"] != "success":
            return generated

        code = generated["code"]

        result = {
            "status": "success",
            "code": code,
        }

        # --------------------------------------------------
        # Step 2 : Save file (optional)
        # --------------------------------------------------

        if path:

            file_tool = self.get_tool(self.FILE_TOOL)

            save = await file_tool.execute(
                {
                    "action": "write_file",
                    "path": path,
                    "content": code,
                }
            )

            if save["status"] != "success":
                return save

            result["path"] = path

        # --------------------------------------------------
        # Step 3 : Execute (optional)
        # --------------------------------------------------

        if auto_run and path:

            runner = self.get_tool(self.RUN_TOOL)

            execution = await runner.execute(
                {
                    "path": path
                }
            )

            result["execution"] = execution

        return result