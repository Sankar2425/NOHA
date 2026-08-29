import json
from urllib import response
import re

from runtime.ai.ollama_client import OllamaClient


class Planner:

    def __init__(self):
        self.llm = OllamaClient()

    async def create_plan(self, command: str):

        prompt = f"""
You are an AI task planner.

Your job is to convert user requests into a JSON array of tool calls.

Return ONLY valid JSON.

Never explain.
Never use markdown.
Never add text before or after the JSON.

AVAILABLE TOOLS

1. file_tool

Actions:
- create_folder
- create_file
- write_file
- read_file
- delete_file
- rename_file
- copy_file
- move_file

2. terminal_tool

Actions:
- execute terminal commands
- open applications

Examples:

Open Chrome

[
    {{
        "tool": "terminal_tool",
        "payload": {{
            "command": "start chrome"
        }}
    }}
]

Open Spotify

[
    {{
        "tool": "terminal_tool",
        "payload": {{
            "command": "start spotify"
        }}
    }}
]

Open Discord

[
    {{
        "tool": "terminal_tool",
        "payload": {{
            "command": "start discord"
        }}
    }}
]

3. memory_tool

Actions:
- remember
- recall
- forget
- list

4. open_website

Actions:
- open websites

IMPORTANT RULES

- Never invent tools.
- Never use code_tool.
- Never use write_code.
- Never use run_code.
- Only use tools listed above.
- If creating files inside folders, use Folder/FileName format.

Tool: code_tool

Purpose:
Generate source code and save it into files.

Payload:

{
    {
    "action": "generate_code",
    "file_name": "example.py",
    "prompt": "Create a Python hello world program"
    }
}



IMPORTANT

If the user asks for source code inside a file:

Use code_tool.

Do NOT use create_file + write_file.

Examples:

calculator.py containing calculator code
→ code_tool

main.py containing flask code
→ code_tool

testing/app.py containing python code
→ code_tool

Any request containing:

- code
- program
- script
- calculator
- python file
- application

should prefer code_tool.

Example 1

User:
Create a folder called test and create a file notes.txt and write hello world to it

Output:

[
    {{
        "tool": "file_tool",
        "payload": {{
            "action": "create_folder",
            "name": "test"
        }}
    }},
    {{
        "tool": "file_tool",
        "payload": {{
            "action": "create_file",
            "name": "notes.txt"
        }}
    }},
    {{
        "tool": "file_tool",
        "payload": {{
            "action": "write_file",
            "name": "notes.txt",
            "content": "hello world"
        }}
    }}
]

Example 2

User:
Create a project called Calculator and create main.py inside it

Output:

[
    {{
        "tool": "file_tool",
        "payload": {{
            "action": "create_folder",
            "name": "Calculator"
        }}
    }},
    {{
        "tool": "file_tool",
        "payload": {{
            "action": "create_file",
            "name": "Calculator/main.py"
        }}
    }}
]

Example 3

User:
Create a project called WebApp and create index.html and style.css inside it

Output:

[
    {{
        "tool": "file_tool",
        "payload": {{
            "action": "create_folder",
            "name": "WebApp"
        }}
    }},
    {{
        "tool": "file_tool",
        "payload": {{
            "action": "create_file",
            "name": "WebApp/index.html"
        }}
    }},
    {{
        "tool": "file_tool",
        "payload": {{
            "action": "create_file",
            "name": "WebApp/style.css"
        }}
    }}
]


User:
Create hello.py containing a hello world program

Output:

[
  {{
    "tool": "code_tool",
    "payload": {{
      "action": "generate_code",
      "file_name": "hello.py",
      "prompt": "Create a Python hello world program"
    }}
  }}
]

User:
Create calculator.py and write a calculator program

Output:

[
  {{
    "tool": "code_tool",
    "payload": {{
      "action": "generate_code",
      "file_name": "calculator.py",
      "prompt": "Create a Python calculator program"
    }}
  }}
]


User:
Create a folder called testing and inside it create first_test.py containing a calculator program

Output:

[
  {{
    "tool": "file_tool",
    "payload": {{
      "action": "create_folder",
      "name": "testing"
    }}
  }},
  {{
    "tool": "code_tool",
    "payload": {{
      "action": "generate_code",
      "file_name": "testing/first_test.py",
      "prompt": "Create a Python calculator program"
    }}
  }}
]


User:
{command}
"""
        response = await self.llm.generate(prompt)

        print("\nPLANNER RESPONSE:")
        print(response)

        match = re.search(
            r"\[.*\]",
            response,
            re.DOTALL
        )

        if not match:
            print("NO PLAN FOUND")
            return []

        plan_text = match.group()

        print("\nEXTRACTED PLAN:")
        print(plan_text)

        return json.loads(plan_text)