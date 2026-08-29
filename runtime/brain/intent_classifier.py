from __future__ import annotations

import json
import re
from typing import Any

from runtime.brain.enums import (
    IntentType,
    SkillType,
    TaskAction,
)
from runtime.brain.models import (
    IntentResult,
    IntentTask,
)


class IntentClassifier:
    """
    LLM-powered intent classifier.

    Responsibilities
    ----------------
    1. Build the NOHA intent-classification prompt.
    2. Send the prompt to Ollama.
    3. Parse the LLM response as JSON.
    4. Validate the NOHA protocol.
    5. Validate skill/action compatibility.
    6. Convert the validated data into IntentResult.

    It does NOT:
    - Execute tasks.
    - Access filesystem tools.
    - Run terminal commands.
    - Open applications.
    - Modify user data.

    The classifier only determines WHAT NOHA should do.
    """

    PROTOCOL_VERSION = 1

    # ==========================================================
    # SKILL → ACTION COMPATIBILITY
    # ==========================================================

    SKILL_ACTIONS: dict[SkillType, set[TaskAction]] = {

        SkillType.FILESYSTEM: {
            TaskAction.CREATE_FOLDER,
            TaskAction.CREATE_FILE,
            TaskAction.WRITE_FILE,
            TaskAction.READ_FILE,
            TaskAction.DELETE_FILE,
            TaskAction.RENAME_FILE,
            TaskAction.COPY_FILE,
            TaskAction.MOVE_FILE,
            TaskAction.LIST_FILES,
        },

        SkillType.CODING: {
            TaskAction.GENERATE_CODE,
            TaskAction.MODIFY_CODE,
            TaskAction.ANALYZE_CODE,
            TaskAction.RUN_CODE,
        },

        SkillType.TERMINAL: {
            TaskAction.RUN_COMMAND,
        },

        SkillType.BROWSER: {
            TaskAction.OPEN_URL,
            TaskAction.SEARCH_WEB,
        },

        SkillType.MEMORY: {
            TaskAction.SAVE_MEMORY,
            TaskAction.LOAD_MEMORY,
            TaskAction.DELETE_MEMORY,
            TaskAction.LIST_MEMORY,
        },

        SkillType.VISION: {
            TaskAction.ANALYZE_IMAGE,
        },

        SkillType.VOICE: {
            TaskAction.SPEAK,
            TaskAction.LISTEN,
        },

        SkillType.CHAT: {
            TaskAction.UNKNOWN,
        },

        # Automation currently has no dedicated action in
        # TaskAction. This remains intentionally empty until
        # the automation action system is implemented.
        SkillType.AUTOMATION: set(),
    }

    # ==========================================================
    # CONSTRUCTOR
    # ==========================================================

    def __init__(self, ollama_client) -> None:
        self.ollama = ollama_client

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    async def classify(self, command: str) -> IntentResult:
        """
        Convert a natural-language command into a validated
        IntentResult.
        """

        if not isinstance(command, str):
            raise TypeError("Command must be a string.")

        command = command.strip()

        if not command:
            raise ValueError("Command cannot be empty.")

        try:
            # --------------------------------------------------
            # 1. Build prompt
            # --------------------------------------------------

            prompt = self._build_prompt(command)

            # --------------------------------------------------
            # 2. Query Ollama
            # --------------------------------------------------

            response = await self._query_llm(prompt)

            # --------------------------------------------------
            # 3. Parse JSON
            # --------------------------------------------------

            data = self._parse_json(response)

            # --------------------------------------------------
            # 4. Validate protocol
            # --------------------------------------------------

            validated = self._validate(data)

            # --------------------------------------------------
            # 5. Build IntentResult
            # --------------------------------------------------

            return self._build_result(
                validated,
                command=command,
                raw_response=data,
            )

        except Exception as exc:
            raise RuntimeError(
                f"Intent classification failed: {exc}"
            ) from exc

    # ==========================================================
    # PROMPT BUILDER
    # ==========================================================

    def _build_prompt(self, command: str) -> str:
        """
        Build the complete deterministic prompt sent to Ollama.
        """

        # ------------------------------------------------------
        # Identity
        # ------------------------------------------------------

        identity = """
# SYSTEM IDENTITY

You are NOHA.

NOHA is an offline AI desktop assistant.

Your responsibility is to understand a user's natural-language
command and convert it into a structured execution plan.

You are NOT a conversational chatbot.

You must NOT execute anything yourself.

You must NOT explain your answer outside the JSON object.

Your output will be consumed directly by the NOHA runtime.
"""

        # ------------------------------------------------------
        # Capabilities
        # ------------------------------------------------------

        capabilities = """
# CAPABILITIES

You can:

- Understand natural-language commands.
- Identify the user's primary goal.
- Break complex commands into ordered tasks.
- Select the appropriate skill.
- Select the appropriate action.
- Extract required parameters.
- Preserve task dependencies and execution order.
- Estimate confidence.
- Return structured JSON.
"""

        # ------------------------------------------------------
        # Available skills
        # ------------------------------------------------------

        available_skills = "\n".join(
            f"- {skill.value}"
            for skill in SkillType
        )

        skills = f"""
# AVAILABLE SKILLS

You may ONLY use these skills:

{available_skills}
"""

        # ------------------------------------------------------
        # Available actions
        # ------------------------------------------------------

        available_actions = "\n".join(
            f"- {action.value}"
            for action in TaskAction
        )

        actions = f"""
# AVAILABLE ACTIONS

You may ONLY use these actions:

{available_actions}
"""

        # ------------------------------------------------------
        # Skill/action rules
        # ------------------------------------------------------

        compatibility_lines: list[str] = []

        for skill, actions_for_skill in self.SKILL_ACTIONS.items():

            if actions_for_skill:
                actions_text = ", ".join(
                    action.value
                    for action in sorted(
                        actions_for_skill,
                        key=lambda item: item.value,
                    )
                )

                compatibility_lines.append(
                    f"- {skill.value}: {actions_text}"
                )

            else:
                compatibility_lines.append(
                    f"- {skill.value}: no executable actions currently available"
                )

        compatibility = f"""
# SKILL / ACTION COMPATIBILITY

You MUST use only valid skill/action combinations.

{chr(10).join(compatibility_lines)}
"""

        # ------------------------------------------------------
        # Protocol
        # ------------------------------------------------------

        protocol = """
# NOHA PROTOCOL

Return exactly ONE JSON object.

The JSON MUST have this structure:

{
    "protocol_version": 1,
    "goal": "...",
    "intent": "...",
    "tasks": [
        {
            "skill": "...",
            "action": "...",
            "parameters": {}
        }
    ],
    "confidence": 0.95,
    "reasoning": "..."
}

FIELD DEFINITIONS

protocol_version
    Integer protocol version.
    Must be 1.

goal
    High-level objective inferred from the user's request.

intent
    Primary high-level intent category.

tasks
    Ordered list of tasks required to achieve the goal.

skill
    Skill responsible for performing the task.

action
    Specific action to perform.

parameters
    Arguments required by the action.

confidence
    Number between 0.0 and 1.0.

reasoning
    Short explanation of the classification.
"""

        # ------------------------------------------------------
        # Rules
        # ------------------------------------------------------

        rules = """
# RULES

1. Return ONLY valid JSON.

2. Never return Markdown.

3. Never wrap the JSON inside ```json blocks.

4. Never explain your answer outside the JSON object.

5. Never answer conversationally.

6. Never invent a skill.

7. Never invent an action.

8. Never invent a parameter name when the action has an obvious
   required parameter.

9. Use only the available skills.

10. Use only the available actions.

11. Use only valid skill/action combinations.

12. Preserve execution order.

13. Split complex commands into multiple ordered tasks.

14. Every executable task must contain:
    - skill
    - action
    - parameters

15. Parameters must be a JSON object.

16. Confidence must be between 0.0 and 1.0.

17. If uncertain, reduce confidence instead of inventing information.

18. Never execute commands yourself.

19. The runtime will execute the resulting plan.

20. Return exactly one JSON object.

21. Always follow the NOHA protocol.

22. Do not use an action belonging to another skill.

23. When one task depends on another task, preserve that order.

24. Do not generate fake execution results.

25. Do not claim a task has already been executed.

26. For code-generation requests, use the coding skill and
    generate_code action.

27. For writing generated code into a file, use filesystem/write_file
    as a separate task after code generation when appropriate.

28. Do not place filesystem actions under the coding skill.

29. Do not place terminal actions under the filesystem skill.

30. Do not place browser actions under the coding skill.
"""

        # ------------------------------------------------------
        # Examples
        # ------------------------------------------------------

        examples = """
# EXAMPLES

Example 1

User:
Create a folder called AI.

Response:

{
    "protocol_version": 1,
    "goal": "Create a folder named AI",
    "intent": "filesystem",
    "tasks": [
        {
            "skill": "filesystem",
            "action": "create_folder",
            "parameters": {
                "path": "AI"
            }
        }
    ],
    "confidence": 0.99,
    "reasoning": "The user wants to create a single folder."
}


Example 2

User:
Create a folder called projects and inside it create notes.txt.

Response:

{
    "protocol_version": 1,
    "goal": "Create a projects folder and a notes.txt file inside it",
    "intent": "filesystem",
    "tasks": [
        {
            "skill": "filesystem",
            "action": "create_folder",
            "parameters": {
                "path": "projects"
            }
        },
        {
            "skill": "filesystem",
            "action": "create_file",
            "parameters": {
                "path": "projects/notes.txt"
            }
        }
    ],
    "confidence": 0.98,
    "reasoning": "The file depends on the projects folder being created first."
}


Example 3

User:
Write a Python program that calculates the factorial of a number.

Response:

{
    "protocol_version": 1,
    "goal": "Generate a Python factorial program",
    "intent": "coding",
    "tasks": [
        {
            "skill": "coding",
            "action": "generate_code",
            "parameters": {
                "language": "python",
                "prompt": "Create a Python program that calculates the factorial of a number."
            }
        }
    ],
    "confidence": 0.99,
    "reasoning": "The user explicitly requested generation of Python code."
}


Example 4

User:
Open YouTube.

Response:

{
    "protocol_version": 1,
    "goal": "Open YouTube",
    "intent": "browser",
    "tasks": [
        {
            "skill": "browser",
            "action": "open_url",
            "parameters": {
                "url": "https://www.youtube.com"
            }
        }
    ],
    "confidence": 0.98,
    "reasoning": "The user wants to open a website."
}


Example 5

User:
Run the Python file calculator.py.

Response:

{
    "protocol_version": 1,
    "goal": "Run calculator.py",
    "intent": "coding",
    "tasks": [
        {
            "skill": "coding",
            "action": "run_code",
            "parameters": {
                "path": "calculator.py"
            }
        }
    ],
    "confidence": 0.97,
    "reasoning": "The user wants to execute a Python source file."
}


Example 6

User:
Create a folder called test, create app.py inside it, and write a Python calculator program into the file.

Response:

{
    "protocol_version": 1,
    "goal": "Create a Python calculator application inside a test folder",
    "intent": "filesystem",
    "tasks": [
        {
            "skill": "filesystem",
            "action": "create_folder",
            "parameters": {
                "path": "test"
            }
        },
        {
            "skill": "filesystem",
            "action": "create_file",
            "parameters": {
                "path": "test/app.py"
            }
        },
        {
            "skill": "coding",
            "action": "generate_code",
            "parameters": {
                "language": "python",
                "prompt": "Create a Python calculator program."
            }
        },
        {
            "skill": "filesystem",
            "action": "write_file",
            "parameters": {
                "path": "test/app.py",
                "content": "$TASK_3_OUTPUT"
            }
        }
    ],
    "confidence": 0.96,
    "reasoning": "The folder and file must exist before generated code can be written into the file."
}
"""

        # ------------------------------------------------------
        # User command
        # ------------------------------------------------------

        user_command = f"""
# USER COMMAND

{command}
"""

        # ------------------------------------------------------
        # Assemble
        # ------------------------------------------------------

        sections = [
            identity,
            capabilities,
            skills,
            actions,
            compatibility,
            protocol,
            rules,
            examples,
            user_command,
        ]

        return "\n\n".join(
            section.strip()
            for section in sections
        )

    # ==========================================================
    # OLLAMA
    # ==========================================================

    async def _query_llm(self, prompt: str) -> str:
        """
        Send the prompt to the Ollama client.

        OllamaClient is responsible only for communication.
        """

        response = await self.ollama.generate(prompt)

        if not isinstance(response, str):
            raise TypeError(
                "Ollama client returned a non-string response."
            )

        response = response.strip()

        if not response:
            raise ValueError(
                "Ollama returned an empty response."
            )

        return response

    # ==========================================================
    # JSON PARSER
    # ==========================================================

    def _parse_json(self, response: str) -> dict[str, Any]:
        """
        Parse JSON returned by the LLM.

        Handles:
        - normal JSON
        - ```json fenced JSON
        - accidental surrounding text
        """

        if not isinstance(response, str):
            raise TypeError(
                "LLM response must be a string."
            )

        text = response.strip()

        if not text:
            raise ValueError(
                "LLM response is empty."
            )

        # ------------------------------------------------------
        # Remove Markdown code fences
        # ------------------------------------------------------

        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\s*```$",
            "",
            text,
        )

        text = text.strip()

        # ------------------------------------------------------
        # First attempt: direct JSON
        # ------------------------------------------------------

        try:
            data = json.loads(text)

        except json.JSONDecodeError:

            # --------------------------------------------------
            # Second attempt:
            # Extract the first JSON object.
            # --------------------------------------------------

            start = text.find("{")
            end = text.rfind("}")

            if start == -1 or end == -1 or end <= start:
                raise ValueError(
                    "LLM response does not contain a valid JSON object."
                )

            json_text = text[start:end + 1]

            try:
                data = json.loads(json_text)

            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Unable to parse LLM JSON response: {exc}"
                ) from exc

        if not isinstance(data, dict):
            raise TypeError(
                "LLM JSON response must be an object."
            )

        return data

    # ==========================================================
    # VALIDATION
    # ==========================================================

    def _validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate and sanitize the NOHA protocol.

        This is the deterministic safety boundary between
        probabilistic LLM output and the runtime.
        """

        if not isinstance(data, dict):
            raise TypeError(
                "Intent response must be a dictionary."
            )

        # ------------------------------------------------------
        # Protocol version
        # ------------------------------------------------------

        protocol_version = data.get("protocol_version")

        if protocol_version != self.PROTOCOL_VERSION:
            raise ValueError(
                "Unsupported or missing protocol_version."
            )

        # ------------------------------------------------------
        # Goal
        # ------------------------------------------------------

        goal = data.get("goal")

        if not isinstance(goal, str) or not goal.strip():
            raise ValueError(
                "Intent response must contain a valid goal."
            )

        # ------------------------------------------------------
        # Intent
        # ------------------------------------------------------

        intent = self._parse_enum(
            IntentType,
            data.get("intent"),
            "intent",
        )

        # ------------------------------------------------------
        # Tasks
        # ------------------------------------------------------

        tasks = data.get("tasks")

        if not isinstance(tasks, list):
            raise TypeError(
                "Intent response 'tasks' must be a list."
            )

        # Unknown/chat requests may legitimately have no
        # executable task.
        if not tasks and intent not in {
            IntentType.UNKNOWN,
            IntentType.CHAT,
        }:
            raise ValueError(
                "Executable intents must contain at least one task."
            )

        validated_tasks: list[dict[str, Any]] = []

        for index, task in enumerate(tasks, start=1):

            if not isinstance(task, dict):
                raise TypeError(
                    f"Task {index} must be an object."
                )

            # --------------------------------------------------
            # Required task fields
            # --------------------------------------------------

            if "skill" not in task:
                raise ValueError(
                    f"Task {index} is missing 'skill'."
                )

            if "action" not in task:
                raise ValueError(
                    f"Task {index} is missing 'action'."
                )

            if "parameters" not in task:
                raise ValueError(
                    f"Task {index} is missing 'parameters'."
                )

            # --------------------------------------------------
            # Skill
            # --------------------------------------------------

            skill = self._parse_enum(
                SkillType,
                task["skill"],
                f"task {index} skill",
            )

            # --------------------------------------------------
            # Action
            # --------------------------------------------------

            action = self._parse_enum(
                TaskAction,
                task["action"],
                f"task {index} action",
            )

            # --------------------------------------------------
            # Parameters
            # --------------------------------------------------

            parameters = task["parameters"]

            if not isinstance(parameters, dict):
                raise TypeError(
                    f"Task {index} parameters must be an object."
                )

            # --------------------------------------------------
            # Skill/action compatibility
            # --------------------------------------------------

            allowed_actions = self.SKILL_ACTIONS.get(
                skill,
                set(),
            )

            if action not in allowed_actions:

                raise ValueError(
                    f"Invalid skill/action combination in task "
                    f"{index}: "
                    f"{skill.value} + {action.value}"
                )

            # --------------------------------------------------
            # Validate action-specific parameters
            # --------------------------------------------------

            self._validate_parameters(
                action=action,
                parameters=parameters,
                task_index=index,
            )

            validated_tasks.append(
                {
                    "skill": skill.value,
                    "action": action.value,
                    "parameters": parameters,
                }
            )

        # ------------------------------------------------------
        # Confidence
        # ------------------------------------------------------

        confidence = data.get("confidence")

        if isinstance(confidence, bool):
            raise TypeError(
                "Confidence must be a number."
            )

        if not isinstance(confidence, (int, float)):
            raise TypeError(
                "Confidence must be a number."
            )

        confidence = float(confidence)

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                "Confidence must be between 0.0 and 1.0."
            )

        # ------------------------------------------------------
        # Reasoning
        # ------------------------------------------------------

        reasoning = data.get("reasoning", "")

        if not isinstance(reasoning, str):
            raise TypeError(
                "Reasoning must be a string."
            )

        # ------------------------------------------------------
        # Return sanitized protocol
        # ------------------------------------------------------

        return {
            "protocol_version": self.PROTOCOL_VERSION,
            "goal": goal.strip(),
            "intent": intent.value,
            "tasks": validated_tasks,
            "confidence": confidence,
            "reasoning": reasoning.strip(),
        }

    # ==========================================================
    # ENUM PARSER
    # ==========================================================

    @staticmethod
    def _parse_enum(
        enum_type,
        value: Any,
        field_name: str,
    ):
        """
        Convert an LLM string into an enum value.

        Supports both:
            "create_file"

        and:
            "CREATE_FILE"

        This makes the protocol more tolerant of normal LLM
        formatting differences without allowing arbitrary values.
        """

        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string."
            )

        normalized = value.strip().lower()

        for member in enum_type:

            if normalized == member.value.lower():
                return member

            if normalized == member.name.lower():
                return member

        raise ValueError(
            f"Invalid {field_name}: {value!r}"
        )

    # ==========================================================
    # PARAMETER VALIDATION
    # ==========================================================

    @staticmethod
    def _validate_parameters(
        action: TaskAction,
        parameters: dict[str, Any],
        task_index: int,
    ) -> None:
        """
        Validate the minimum required parameters for each action.

        This does not execute anything.
        """

        required_parameters: dict[TaskAction, set[str]] = {

            TaskAction.CREATE_FOLDER: {
                "path",
            },

            TaskAction.CREATE_FILE: {
                "path",
            },

            TaskAction.WRITE_FILE: {
                "path",
                "content",
            },

            TaskAction.READ_FILE: {
                "path",
            },

            TaskAction.DELETE_FILE: {
                "path",
            },

            TaskAction.RENAME_FILE: {
                "source",
                "destination",
            },

            TaskAction.COPY_FILE: {
                "source",
                "destination",
            },

            TaskAction.MOVE_FILE: {
                "source",
                "destination",
            },

            TaskAction.LIST_FILES: {
                "path",
            },

            TaskAction.GENERATE_CODE: {
                "language",
                "prompt",
            },

            TaskAction.MODIFY_CODE: {
                "path",
                "instruction",
            },

            TaskAction.ANALYZE_CODE: {
                "path",
            },

            TaskAction.RUN_CODE: {
                "path",
            },

            TaskAction.RUN_COMMAND: {
                "command",
            },

            TaskAction.OPEN_URL: {
                "url",
            },

            TaskAction.SEARCH_WEB: {
                "query",
            },

            TaskAction.APPLICATION: {
                "name",
            },

            TaskAction.SAVE_MEMORY: {
                "key",
                "value",
            },

            TaskAction.LOAD_MEMORY: {
                "key",
            },

            TaskAction.DELETE_MEMORY: {
                "key",
            },

            TaskAction.LIST_MEMORY: set(),

            TaskAction.ANALYZE_IMAGE: {
                "path",
            },

            TaskAction.SPEAK: {
                "text",
            },

            TaskAction.LISTEN: set(),

            TaskAction.UNKNOWN: set(),
        }

        required = required_parameters.get(
            action,
            set(),
        )

        missing = [
            parameter
            for parameter in required
            if parameter not in parameters
        ]

        if missing:
            raise ValueError(
                f"Task {task_index} action '{action.value}' "
                f"is missing required parameters: "
                f"{', '.join(sorted(missing))}"
            )

        # ------------------------------------------------------
        # Basic parameter type validation
        # ------------------------------------------------------

        for key, value in parameters.items():

            if not isinstance(key, str):
                raise TypeError(
                    f"Task {task_index} contains a non-string "
                    f"parameter name."
                )

            if value is None:
                raise ValueError(
                    f"Task {task_index} parameter '{key}' "
                    f"cannot be null."
                )

    # ==========================================================
    # BUILD RESULT
    # ==========================================================

    def _build_result(
        self,
        data: dict[str, Any],
        *,
        command: str,
        raw_response: dict[str, Any],
    ) -> IntentResult:
        """
        Convert validated protocol data into IntentResult.
        """

        intent = self._parse_enum(
            IntentType,
            data["intent"],
            "intent",
        )

        intent_tasks: list[IntentTask] = []

        for task_data in data["tasks"]:

            skill = self._parse_enum(
                SkillType,
                task_data["skill"],
                "task skill",
            )

            action = self._parse_enum(
                TaskAction,
                task_data["action"],
                "task action",
            )

            intent_tasks.append(
                IntentTask(
                    skill=skill,
                    action=action,
                    parameters=dict(
                        task_data["parameters"]
                    ),
                )
            )

        return IntentResult(
            goal=data["goal"],
            intent=intent,
            tasks=intent_tasks,
            confidence=data["confidence"],
            reasoning=data["reasoning"],
            command=command,
            raw_response=raw_response,
        )