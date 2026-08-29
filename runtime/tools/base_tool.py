from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """
    Base interface for every NOHA executable tool.

    Tools are responsible for performing one category of
    operations. They do not decide what the user wants and
    they do not manage task planning.
    """

    name: str = ""

    description: str = ""

    @abstractmethod
    async def execute(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute the tool using the supplied payload.

        Parameters
        ----------
        payload:
            Tool-specific input parameters.

        Returns
        -------
        dict:
            Structured execution result.
        """

        raise NotImplementedError