from __future__ import annotations

from runtime.brain.enums import TaskAction
from runtime.memory.memory_store import MemoryStore
from runtime.tools.base_tool import BaseTool


class MemoryTool(BaseTool):
    """
    Stores and retrieves long-term memory.
    """

    name = "memory"
    description = "Stores, recalls, deletes, and lists memories."

    async def execute(
        self,
        payload: dict,
    ) -> dict:

        action = payload.get("action")
        key = payload.get("key")
        value = payload.get("value")

        memory = MemoryStore.load()

        try:

            if action == TaskAction.SAVE_MEMORY.value:

                if not key:
                    return {
                        "status": "error",
                        "message": "Memory key is required."
                    }

                memory[key] = value
                MemoryStore.save(memory)

                return {
                    "status": "success",
                    "message": f"Memory '{key}' saved."
                }

            elif action == TaskAction.LOAD_MEMORY.value:

                if not key:
                    return {
                        "status": "error",
                        "message": "Memory key is required."
                    }

                return {
                    "status": "success",
                    "key": key,
                    "value": memory.get(key)
                }

            elif action == TaskAction.DELETE_MEMORY.value:

                if not key:
                    return {
                        "status": "error",
                        "message": "Memory key is required."
                    }

                memory.pop(key, None)
                MemoryStore.save(memory)

                return {
                    "status": "success",
                    "message": f"Memory '{key}' deleted."
                }

            elif action == TaskAction.LIST_MEMORY.value:

                return {
                    "status": "success",
                    "memories": memory
                }

            return {
                "status": "error",
                "message": f"Unsupported action '{action}'."
            }

        except Exception as exc:

            return {
                "status": "error",
                "message": str(exc)
            }