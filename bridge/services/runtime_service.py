from runtime.core.runtime_engine import RuntimeEngine

runtime = RuntimeEngine()


async def process_command(command: str):

    return await runtime.handle_command(command)