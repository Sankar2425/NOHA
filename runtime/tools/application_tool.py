from __future__ import annotations

import subprocess

from runtime.brain.enums import TaskAction
from runtime.tools.base_tool import BaseTool


class ApplicationTool(BaseTool):
    """
    Tool responsible for managing desktop applications.

    Supported actions:
        - OPEN_APP
        - CLOSE_APP

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

        if action == TaskAction.OPEN_APP.value:
            return self._open(payload)

        if action == TaskAction.CLOSE_APP.value:
            return self._close(payload)

        if action == TaskAction.LIST_RUNNING_APPS.value:
            return self._not_implemented(action)

        if action == TaskAction.FOCUS_APP.value:
            return self._not_implemented(action)

        if action == TaskAction.MINIMIZE_APP.value:
            return self._not_implemented(action)

        if action == TaskAction.MAXIMIZE_APP.value:
            return self._not_implemented(action)

        if action == TaskAction.KILL_APP.value:
            return self._not_implemented(action)

        if action == TaskAction.RESTART_APP.value:
            return self._not_implemented(action)

        return {
            "success": False,
            "message": f"Unsupported action: {action}",
        }

    # ---------------------------------------------------------
    # OPEN APPLICATION
    # ---------------------------------------------------------

    def _open(
        self,
        payload: dict,
    ) -> dict:

        app = payload.get("app", "").strip()

        if not app:
            return {
                "success": False,
                "message": "No application specified.",
            }

        try:

            subprocess.Popen(app)

            return {
                "success": True,
                "message": f"Opened '{app}'.",
                "application": app,
            }

        except Exception as exc:

            return {
                "success": False,
                "message": str(exc),
            }

    # ---------------------------------------------------------
    # CLOSE APPLICATION
    # ---------------------------------------------------------

    def _close(
        self,
        payload: dict,
    ) -> dict:

        process = payload.get("process", "").strip()

        if not process:
            return {
                "success": False,
                "message": "No process specified.",
            }

        try:

            subprocess.run(
                [
                    "taskkill",
                    "/F",
                    "/IM",
                    process,
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            return {
                "success": True,
                "message": f"Closed '{process}'.",
                "process": process,
            }

        except subprocess.CalledProcessError as exc:

            return {
                "success": False,
                "message": exc.stderr.strip(),
            }

        except Exception as exc:

            return {
                "success": False,
                "message": str(exc),
            }

    # ---------------------------------------------------------
    # FUTURE ACTIONS
    # ---------------------------------------------------------

    def _not_implemented(
        self,
        action: str,
    ) -> dict:

        return {
            "success": False,
            "message": f"{action} is not implemented yet.",
        }