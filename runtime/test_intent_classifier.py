import asyncio

from runtime.ai import OllamaClient
from runtime.brain.intent_classifier import IntentClassifier


async def main() -> None:
    # ------------------------------------------------------
    # Create Ollama client
    # ------------------------------------------------------

    ollama = OllamaClient()

    # ------------------------------------------------------
    # Create Intent Classifier
    # ------------------------------------------------------

    classifier = IntentClassifier(ollama)

    # ------------------------------------------------------
    # Test command
    # ------------------------------------------------------

    command = "Create a folder called test, create app.py inside it, and write a Python calculator program into the file"

    print("\n========================================")
    print("NOHA INTENT CLASSIFIER TEST")
    print("========================================")

    print("\nUser command:")
    print(command)

    # ------------------------------------------------------
    # Classify
    # ------------------------------------------------------

    result = await classifier.classify(command)

    # ------------------------------------------------------
    # Display result
    # ------------------------------------------------------

    print("\n----------------------------------------")
    print("INTENT RESULT")
    print("----------------------------------------")

    print(f"Goal       : {result.goal}")
    print(f"Intent     : {result.intent.value}")
    print(f"Confidence : {result.confidence}")
    print(f"Reasoning  : {result.reasoning}")

    print("\nTasks:")

    for index, task in enumerate(result.tasks, start=1):

        print(f"\n  Task {index}")
        print(f"    Skill      : {task.skill.value}")
        print(f"    Action     : {task.action.value}")
        print(f"    Parameters : {task.parameters}")

    print("\n========================================")
    print("CLASSIFICATION SUCCESS")
    print("========================================")


if __name__ == "__main__":
    asyncio.run(main())