import re

from runtime.ai.ollama_client import OllamaClient


class CodeGenerator:

    EXTENSIONS = {
        ".py": "Python",
        ".cpp": "C++",
        ".c": "C",
        ".java": "Java",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".html": "HTML",
        ".css": "CSS",
        ".json": "JSON",
        ".md": "Markdown"
    }

    def __init__(self):
        self.llm = OllamaClient()

    async def generate(
        self,
        request: str,
        file_name: str
    ):

        file_name = file_name.lower()

        language = "Text"

        for ext, lang in self.EXTENSIONS.items():
            if file_name.endswith(ext):
                language = lang
                break

        prompt = f"""
You are a senior {language} software engineer.

Your task is to generate production-quality {language} code.

Filename:
{file_name}

User Request:
{request}

Rules:

- Return ONLY valid {language} source code.
- Never use Markdown.
- Never use triple backticks.
- Never explain the code.
- Never add introductory text.
- The code must be complete.
- The code must compile or run successfully.
- Follow best coding practices.
- If the request is incomplete, make reasonable assumptions.

Return ONLY raw source code.
"""

        response = await self.llm.generate(prompt)

        response = re.sub(
            r"^```[a-zA-Z]*",
            "",
            response.strip()
        )

        response = re.sub(
            r"```$",
            "",
            response.strip()
        )

        response = response.replace(
            "```python",
            ""
        )

        response = response.replace(
            "```",
            ""
        )

        return response.strip()