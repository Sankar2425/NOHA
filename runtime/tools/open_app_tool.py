from __future__ import annotations

import subprocess
from pathlib import Path

from runtime.tools.base_tool import BaseTool


class OpenAppTool(BaseTool):
    """
    Opens an application installed on the system.
    """

    name = "application"
    description = "Launches desktop applications."

    async def execute(
        self,
        payload: dict,
    ) -> dict:

        command = payload.get("command")

        if not command:
            return {
                "status": "error",
                "message": "No application command provided.",
            }

        try:

            subprocess.Popen(command, shell=True)

            return {
                "status": "success",
                "command": command,
                "message": "Application launched.",
            }

        except Exception as exc:

            return {
                "status": "error",
                "message": str(exc),
            }