from __future__ import annotations

from runtime.brain.task import Task
from runtime.skills.base import BaseSkill


class MemorySkill(BaseSkill):
    """
    Skill responsible for long-term memory operations.

    This skill delegates all memory operations
    to the MemoryTool.
    """

    name = "memory"
    description = "Handles memory storage and retrieval."

    TOOL_NAME = "memory_tool"

    async def execute(self, task: Task) -> dict:
        """
        Execute a memory task.
        """

        tool = self.get_tool(self.TOOL_NAME)

        payload = {
            "action": task.action.value,
            **task.payload,
        }

        return await tool.execute(payload)