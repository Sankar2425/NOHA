from __future__ import annotations

from runtime.brain.task import Task
from runtime.skills.base import BaseSkill


class FilesystemSkill(BaseSkill):
    """
    Skill responsible for filesystem operations.

    This skill delegates all work to the FileTool.
    """

    name = "filesystem"
    description = "Handles file and directory operations."

    TOOL_NAME = "file_tool"

    async def execute(self, task: Task) -> dict:
        """
        Execute a filesystem task.
        """

        tool = self.get_tool(self.TOOL_NAME)

        payload = {
            "action": task.action.value,
            **task.payload,
        }

        return await tool.execute(payload)