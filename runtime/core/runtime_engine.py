from __future__ import annotations

from runtime.brain.brain import Brain
from runtime.brain.models import ReflectionResult


class RuntimeEngine:
    """
    Entry point for the NOHA runtime.

    Responsibilities:
        - Receive user commands
        - Forward them to the Brain
        - Return the final result

    All intelligence lives inside the Brain.
    """

    def __init__(self, brain: Brain) -> None:
        self.brain = brain

    async def process(
        self,
        command: str,
    ) -> ReflectionResult:
        """
        Process a user command.
        """

        command = command.strip()

        if not command:
            raise ValueError("Command cannot be empty.")

        return await self.brain.process(command)