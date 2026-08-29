from __future__ import annotations

import subprocess

from runtime.tools.base_tool import BaseTool


class CloseAppTool(BaseTool):
    """
    Closes a running application by process name.
    """

    name = "application"
    description = "Terminates running desktop applications."

    async def execute(
        self,
        payload: dict,
    ) -> dict:

        process = payload.get("process")

        if not process:
            return {
                "status": "error",
                "message": "No process name provided.",
            }

        try:

            result = subprocess.run(
                ["taskkill", "/F", "/IM", process],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return {
                    "status": "success",
                    "process": process,
                    "message": "Application closed.",
                }

            return {
                "status": "error",
                "process": process,
                "message": result.stderr.strip()
                or "Failed to close application.",
            }

        except Exception as exc:

            return {
                "status": "error",
                "message": str(exc),
            }