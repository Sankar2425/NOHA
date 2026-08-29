from __future__ import annotations

from runtime.brain.task import Task
from runtime.skills.base import BaseSkill


class TerminalSkill(BaseSkill):
    """
    Skill responsible for terminal command execution.
    """

    name = "terminal"
    description = "Executes terminal commands."

    TOOL_NAME = "terminal_tool"

    async def execute(self, task: Task) -> dict:
        """
        Execute a terminal task.
        """

        tool = self.get_tool(self.TOOL_NAME)

        payload = {
            "command": task.payload.get("command", "")
        }

        return await tool.execute(payload)