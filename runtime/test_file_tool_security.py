from __future__ import annotations

import asyncio

from runtime.tools.file_tool import FileTool


async def main() -> None:

    print("=" * 50)
    print("NOHA FILE TOOL SECURITY TEST")
    print("=" * 50)

    tool = FileTool()

    # --------------------------------------------------
    # Valid path
    # --------------------------------------------------

    print("\nTesting valid path...")

    result = await tool.execute(
        {
            "action": "create_folder",
            "path": "security_test",
        }
    )

    print(result)

    if result["status"] != "success":
        raise RuntimeError("Valid path test failed.")

    print("[OK] Valid path accepted.")

    # --------------------------------------------------
    # Path traversal
    # --------------------------------------------------

    print("\nTesting path traversal...")

    result = await tool.execute(
        {
            "action": "create_folder",
            "path": "../../outside_workspace",
        }
    )

    print(result)

    if result["status"] == "success":
        raise RuntimeError(
            "SECURITY FAILURE: "
            "Path traversal was allowed."
        )

    print("[OK] Path traversal blocked.")

    # --------------------------------------------------
    # Absolute path
    # --------------------------------------------------

    print("\nTesting absolute path...")

    result = await tool.execute(
        {
            "action": "create_folder",
            "path": r"C:\outside_noha",
        }
    )

    print(result)

    if result["status"] == "success":
        raise RuntimeError(
            "SECURITY FAILURE: "
            "Absolute path escaped workspace."
        )

    print("[OK] Absolute path blocked.")

    print("\n" + "=" * 50)
    print("FILE TOOL SECURITY TEST SUCCESS")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())