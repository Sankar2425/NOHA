import asyncio

from runtime.ai.code_generator import CodeGenerator


async def main():

    generator = CodeGenerator()

    code = await generator.generate(
        "Create a Python hello world program"
    )

    print("\nGENERATED CODE:\n")
    print(code)


asyncio.run(main())