from __future__ import annotations

import subprocess

from runtime.security.command_guard import CommandGuard
from runtime.tools.base_tool import BaseTool


class TerminalTool(BaseTool):
    """
    Executes safe terminal commands.
    """

    name = "terminal"
    description = "Executes safe terminal commands."

    async def execute(
        self,
        payload: dict,
    ) -> dict:

        command = payload.get("command", "").strip()

        if not command:
            return {
                "status": "error",
                "message": "No command provided.",
            }

        if not CommandGuard.is_allowed_terminal_command(command):
            return {
                "status": "error",
                "message": "Command blocked by security policy.",
            }

        try:

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": "Command completed successfully.",
                    "command": command,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode,
                }

            return {
                "status": "error",
                "message": "Command exited with a non-zero status.",
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }

        except Exception as exc:

            return {
                "status": "error",
                "message": str(exc),
            }
