from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from runtime.tools.base_tool import BaseTool


class RunCodeTool(BaseTool):
    """
    Executes source code files inside the workspace.
    """

    name = "run_code"
    description = "Executes source code files."

    WORKSPACE = Path("workspace")

    async def execute(
        self,
        payload: dict,
    ) -> dict:

        path = payload.get("path")

        if not path:
            return {
                "status": "error",
                "message": "No file path provided.",
            }

        file_path = self.WORKSPACE / path

        if not file_path.exists():
            return {
                "status": "error",
                "message": f"File not found: {path}",
            }

        suffix = file_path.suffix.lower()

        try:

            if suffix == ".py":

                result = subprocess.run(
                    [sys.executable, str(file_path)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

            else:

                return {
                    "status": "error",
                    "message": (
                        f"Unsupported file type '{suffix}'."
                    ),
                }

            return {
                "status": "success",
                "success": result.returncode == 0,
                "path": path,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }

        except subprocess.TimeoutExpired:

            return {
                "status": "error",
                "message": "Execution timed out.",
            }

        except Exception as exc:

            return {
                "status": "error",
                "message": str(exc),
            }