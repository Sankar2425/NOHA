from __future__ import annotations

from typing import Dict

from runtime.skills.base import BaseSkill


class SkillRegistry:
    """
    Stores and provides access to all registered skills.
    """

    def __init__(self) -> None:
        self._skills: Dict[str, BaseSkill] = {}

    def register(self, skill: BaseSkill) -> "SkillRegistry":
        """
        Register a skill instance.
        """

        if not skill.name:
            raise ValueError(
                f"{skill.__class__.__name__} must define a skill name."
            )

        if skill.name in self._skills:
            raise ValueError(
                f"Skill '{skill.name}' is already registered."
            )

        self._skills[skill.name] = skill
        return self

    def get(self, name: str) -> BaseSkill | None:
        """
        Retrieve a registered skill.
        """

        return self._skills.get(name)

    def has(self, name: str) -> bool:
        """
        Check if a skill exists.
        """

        return name in self._skills

    def unregister(self, name: str) -> None:
        """
        Remove a registered skill.
        """

        self._skills.pop(name, None)

    def clear(self) -> None:
        """
        Remove all registered skills.
        """

        self._skills.clear()

    def all(self) -> dict[str, BaseSkill]:
        """
        Return all registered skills.
        """

        return self._skills.copy()

    def names(self) -> list[str]:
        """
        Return registered skill names.
        """

        return sorted(self._skills.keys())