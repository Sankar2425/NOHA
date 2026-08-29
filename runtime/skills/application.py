from __future__ import annotations

from runtime.brain.enums import SkillType
from runtime.brain.task import Task
from runtime.skills.base import BaseSkill


class ApplicationSkill(BaseSkill):
    """
    Skill responsible for application management.

    This skill delegates all application-related operations
    to the ApplicationTool.
    """

    name = SkillType.APPLICATION.value

    TOOL_NAME = "application"

    async def execute(
        self,
        task: Task,
    ) -> dict:

        tool = self.get_tool(self.TOOL_NAME)

        payload = {
            "action": task.action.value,
            **task.payload,
        }

        return await tool.execute(payload)