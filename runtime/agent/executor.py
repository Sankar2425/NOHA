from runtime.tools.tool_registry import TOOLS


class Executor:

    async def execute_plan(self, plan):

        results = []

        for step in plan:

            tool_name = step.get("tool")
            payload = step.get("payload", {})

            tool = TOOLS.get(tool_name)

            if not tool:

                results.append({
                    "status": "error",
                    "message": f"Tool not found: {tool_name}"
                })

                continue

            result = await tool.execute(payload)

            results.append(result)

        return results