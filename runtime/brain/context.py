from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BrainContext:
    """
    Stores the current session context.

    This allows NOHA to understand follow-up commands without
    asking the user to repeat information.
    """

    # Workspace information
    current_workspace: str = ""
    current_project: str = ""
    current_folder: str = ""
    current_file: str = ""

    # Conversation information
    conversation_goal: str = ""
    last_user_command: str = ""
    last_response: str = ""

    # Execution history
    previous_task_id: str | None = None
    previous_skill: str = ""

    # Arbitrary session variables
    variables: dict[str, Any] = field(default_factory=dict)

    def set_variable(self, key: str, value: Any) -> None:
        self.variables[key] = value

    def get_variable(self, key: str, default: Any = None) -> Any:
        return self.variables.get(key, default)

    def remove_variable(self, key: str) -> None:
        self.variables.pop(key, None)

    def clear(self) -> None:
        self.current_workspace = ""
        self.current_project = ""
        self.current_folder = ""
        self.current_file = ""

        self.conversation_goal = ""
        self.last_user_command = ""
        self.last_response = ""

        self.previous_task_id = None
        self.previous_skill = ""

        self.variables.clear()