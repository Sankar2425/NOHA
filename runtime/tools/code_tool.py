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

        if not prompt:
            return {
                "status": "error",
                "message": "No prompt provided."
            }

        try:

            code = await self.generator.generate(prompt)

            return {
                "status": "success",
                "code": code,
                "prompt": prompt,
            }

        except Exception as exc:

            return {
                "status": "error",
                "message": str(exc),
            }