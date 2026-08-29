from __future__ import annotations

from runtime.brain.enums import SkillType
from runtime.tools.tool_registry import ToolRegistry


def main() -> None:

    print("=" * 50)
    print("NOHA TOOL REGISTRY TEST")
    print("=" * 50)

    # ------------------------------------------------------
    # Create registry
    # ------------------------------------------------------

    registry = ToolRegistry()

    print("\nRegistered tools:")

    for tool in registry.list_details():
        print(
            f"\n  Skill      : {tool['skill']}"
            f"\n  Tool       : {tool['name']}"
            f"\n  Description: {tool['description']}"
        )

    # ------------------------------------------------------
    # Test expected tools
    # ------------------------------------------------------

    expected_skills = [
        SkillType.FILESYSTEM,
        SkillType.CODING,
        SkillType.BROWSER,
        SkillType.MEMORY,
        SkillType.TERMINAL,
        SkillType.APPLICATION,
    ]

    print("\n" + "-" * 50)
    print("Checking expected skills...")
    print("-" * 50)

    for skill in expected_skills:

        if registry.has(skill):
            print(f"  [OK] {skill.value}")
        else:
            print(f"  [FAIL] {skill.value}")
            raise RuntimeError(
                f"Missing tool for skill: {skill.value}"
            )

    # ------------------------------------------------------
    # Test lookup
    # ------------------------------------------------------

    print("\n" + "-" * 50)
    print("Testing tool lookup...")
    print("-" * 50)

    filesystem_tool = registry.get(
        SkillType.FILESYSTEM
    )

    print(
        f"  Filesystem tool: "
        f"{filesystem_tool.name}"
    )

    coding_tool = registry.get(
        SkillType.CODING
    )

    print(
        f"  Coding tool: "
        f"{coding_tool.name}"
    )

    # ------------------------------------------------------
    # Test execution adapter
    # ------------------------------------------------------

    print("\n" + "-" * 50)
    print("Testing registry execution adapter...")
    print("-" * 50)

    import asyncio

    result = asyncio.run(
        registry.execute(
            skill=SkillType.FILESYSTEM,
            action="create_folder",
            payload={
                "path": "registry_test"
            },
        )
    )

    print(f"\n  Result: {result}")

    if result.get("status") != "success":
        raise RuntimeError(
            "Filesystem registry execution failed."
        )

    # ------------------------------------------------------
    # Success
    # ------------------------------------------------------

    print("\n" + "=" * 50)
    print("TOOL REGISTRY SUCCESS")
    print("=" * 50)


if __name__ == "__main__":
    main()