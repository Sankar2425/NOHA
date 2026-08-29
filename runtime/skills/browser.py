from __future__ import annotations

from runtime.brain.task import Task
from runtime.skills.base import BaseSkill


class BrowserSkill(BaseSkill):
    """
    Skill responsible for browser-related operations.
    """

    name = "browser"
    description = "Handles browser operations."

    TOOL_NAME = "browser"

    async def execute(self, task: Task) -> dict:
        """
        Execute a browser task.
        """

        tool = self.get_tool(self.TOOL_NAME)

        payload = {
            "action": task.action.value,
            **task.payload
        }

        return await tool.execute(payload)