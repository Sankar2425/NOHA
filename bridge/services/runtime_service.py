from runtime.NohaBuilder import RuntimeBuilder

runtime = RuntimeBuilder().build()


async def process_command(command: str):

    return await runtime.process(command)
