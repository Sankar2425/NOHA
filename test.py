import asyncio

from runtime.ai import OllamaClient


async def main():
    client = OllamaClient()

    response = await client.generate(
        "Say hello in one sentence."
    )

    print(response)


asyncio.run(main())