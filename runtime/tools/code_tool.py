from __future__ import annotations

from runtime.ai.code_generator import CodeGenerator
from runtime.tools.base_tool import BaseTool


class CodeTool(BaseTool):
    """
    Generates source code from a natural language prompt.

    This tool ONLY generates code.
    It does not create files or execute programs.
    """

    name = "coding"
    description = "Generates source code."

    def __init__(self) -> None:
        self.generator = CodeGenerator()

    async def execute(
        self,
        payload: dict,
    ) -> dict:

        prompt = payload.get("prompt")
        file_name = payload.get("file_name")

        if not prompt:
            return {
                "status": "error",
                "message": "No prompt provided."
            }

        if file_name is None:
            file_name = self._default_file_name(
                payload.get("language")
            )

        if not isinstance(file_name, str) or not file_name.strip():
            return {
                "status": "error",
                "message": "Code generation file_name must be a non-empty string.",
            }

        try:

            code = await self.generator.generate(
                request=prompt,
                file_name=file_name,
            )

            return {
                "status": "success",
                "code": code,
                "prompt": prompt,
                "file_name": file_name,
            }

        except Exception as exc:

            return {
                "status": "error",
                "message": str(exc),
            }

    @staticmethod
    def _default_file_name(language: object) -> str:
        """Provide a safe language hint for standalone code requests."""

        extensions = {
            "python": ".py",
            "c++": ".cpp",
            "c": ".c",
            "java": ".java",
            "javascript": ".js",
            "typescript": ".ts",
            "html": ".html",
            "css": ".css",
            "json": ".json",
            "markdown": ".md",
        }

        normalized = str(language or "").strip().lower()

        return f"generated{extensions.get(normalized, '.txt')}"
