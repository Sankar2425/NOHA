from __future__ import annotations

import subprocess

from runtime.brain.enums import TaskAction
from runtime.tools.base_tool import BaseTool


class ApplicationTool(BaseTool):
    """
    Tool responsible for managing desktop applications.

    Supported action:
        - application

    Future:
        - LIST_RUNNING_APPS
        - FOCUS_APP
        - MINIMIZE_APP
        - MAXIMIZE_APP
        - KILL_APP
        - RESTART_APP
    """

    name = "application"

    async def execute(
        self,
        payload: dict,
    ) -> dict:

        action = payload.get("action")

        if action == TaskAction.APPLICATION.value:
            return self._open(payload)

        return {
            "status": "error",
            "message": f"Unsupported action: {action}",
        }

    # ---------------------------------------------------------
    # OPEN APPLICATION
    # ---------------------------------------------------------

    def _open(
        self,
        payload: dict,
    ) -> dict:

        app = payload.get("name", payload.get("app", "")).strip()

        if not app:
            return {
                "status": "error",
                "message": "No application specified.",
            }

        try:

            subprocess.Popen(app)

            return {
                "status": "success",
                "message": f"Opened '{app}'.",
                "application": app,
            }

        except Exception as exc:

            return {
                "status": "error",
                "message": str(exc),
            }
