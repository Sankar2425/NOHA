import asyncio

from runtime.ai.code_generator import CodeGenerator


async def main():

    generator = CodeGenerator()

    code = await generator.generate(
        request="Create a Python hello world program",
        file_name="hello.py",
    )

    print("\nGENERATED CODE:\n")
    print(code)


asyncio.run(main())
