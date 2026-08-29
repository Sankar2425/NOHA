from __future__ import annotations

from typing import Any

from runtime.brain.enums import SkillType
from runtime.tools.base_tool import BaseTool
from runtime.tools.file_tool import FileTool
from runtime.tools.code_tool import CodeTool
from runtime.tools.browser_tool import BrowserTool
from runtime.tools.memory_tool import MemoryTool
from runtime.tools.terminal_tool import TerminalTool
from runtime.tools.system_info_tool import SystemInfoTool
from runtime.tools.open_app_tool import OpenAppTool
from runtime.tools.close_app_tool import CloseAppTool
from runtime.tools.open_website_tool import OpenWebsiteTool
from runtime.tools.run_code_tool import RunCodeTool
from runtime.tools.application_tool import ApplicationTool


class ToolRegistry:
    """
    Central registry for all executable NOHA tools.

    Responsibilities
    ----------------
    - Register tools.
    - Look up tools by skill.
    - Prevent duplicate registrations.
    - Provide a single interface for the Executor.

    The registry does NOT:
    - plan tasks
    - execute tasks itself
    - interpret natural language
    - decide user intent
    """

    def __init__(
        self,
        auto_register: bool = True,
    ) -> None:

        self._tools: dict[str, BaseTool] = {}

        if auto_register:
            self._register_default_tools()

    # ==========================================================
    # REGISTRATION
    # ==========================================================

    def register(
        self,
        skill: SkillType | str,
        tool: BaseTool,
    ) -> None:
        """
        Register a tool for a skill.
        """

        if isinstance(skill, SkillType):
            skill_name = skill.value
        else:
            skill_name = str(skill)

        if not skill_name.strip():
            raise ValueError(
                "Tool skill name cannot be empty."
            )

        if not isinstance(tool, BaseTool):
            raise TypeError(
                "Registered tool must inherit from BaseTool."
            )

        if skill_name in self._tools:
            raise ValueError(
                f"A tool is already registered for "
                f"skill '{skill_name}'."
            )

        self._tools[skill_name] = tool

    # ==========================================================
    # LOOKUP
    # ==========================================================

    def get(
        self,
        skill: SkillType | str,
    ) -> BaseTool:
        """
        Retrieve a tool registered for a skill.
        """

        if isinstance(skill, SkillType):
            skill_name = skill.value
        else:
            skill_name = str(skill)

        tool = self._tools.get(skill_name)

        if tool is None:
            raise KeyError(
                f"No tool registered for skill "
                f"'{skill_name}'."
            )

        return tool

    # ==========================================================
    # CHECK
    # ==========================================================

    def has(
        self,
        skill: SkillType | str,
    ) -> bool:
        """
        Check whether a tool exists for a skill.
        """

        if isinstance(skill, SkillType):
            skill_name = skill.value
        else:
            skill_name = str(skill)

        return skill_name in self._tools

    # ==========================================================
    # LIST
    # ==========================================================

    def list_tools(self) -> list[str]:
        """
        Return all registered skill names.
        """

        return sorted(self._tools.keys())

    def list_details(self) -> list[dict[str, str]]:
        """
        Return information about registered tools.
        """

        return [
            {
                "skill": skill,
                "name": tool.name,
                "description": tool.description,
            }
            for skill, tool in sorted(
                self._tools.items()
            )
        ]

    # ==========================================================
    # DEFAULT TOOLS
    # ==========================================================

    def _register_default_tools(self) -> None:
        """
        Register NOHA's built-in tools.
        """

        self.register(
            SkillType.FILESYSTEM,
            FileTool(),
        )

        self.register(
            SkillType.CODING,
            CodeTool(),
        )

        self.register(
            SkillType.BROWSER,
            BrowserTool(),
        )

        self.register(
            SkillType.MEMORY,
            MemoryTool(),
        )

        self.register(
            SkillType.TERMINAL,
            TerminalTool(),
        )

        self.register(
            SkillType.APPLICATION,
            ApplicationTool(),
        )

        # ------------------------------------------------------
        # Additional tools
        # ------------------------------------------------------

        # These tools may represent more specific operations
        # rather than independent skills. They are intentionally
        # not registered under separate skill names yet.
        #
        # Executor routing for these will be handled through
        # action-level dispatch where appropriate.

    # ==========================================================
    # EXECUTION ADAPTER
    # ==========================================================

    async def execute(
        self,
        skill: SkillType | str,
        action: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a tool using skill + action + payload.

        The registry adapts the Planner's Task representation
        to the tool's expected payload format.
        """

        tool = self.get(skill)

        tool_payload = dict(
            payload or {}
        )

        # FileTool expects the action inside the payload.
        tool_payload.setdefault(
            "action",
            action,
        )

        try:

            result = await tool.execute(
                tool_payload
            )

        except Exception as exc:

            return {
                "status": "error",
                "message": str(exc),
                "skill": (
                    skill.value
                    if isinstance(skill, SkillType)
                    else str(skill)
                ),
                "action": action,
            }

        if not isinstance(result, dict):

            return {
                "status": "error",
                "message": (
                    "Tool returned an invalid result. "
                    "Expected a dictionary."
                ),
                "skill": (
                    skill.value
                    if isinstance(skill, SkillType)
                    else str(skill)
                ),
                "action": action,
            }

        return result