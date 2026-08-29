from runtime.agent.planner import Planner
from runtime.agent.executor import Executor


class Agent:

    def __init__(self):
        self.planner = Planner()
        self.executor = Executor()

    async def run(self, command: str):

        plan = await self.planner.create_plan(command)

        print("\n===== PLAN =====")
        print(plan)

        results = await self.executor.execute_plan(plan)

        return results