import json
import re

from runtime.ai.ollama_client import OllamaClient


class AIRouter:

    def __init__(self):
        self.llm = OllamaClient()

    async def route(self, command: str):

        prompt = f"""
You are an AI command router.

Your job is to convert user commands into JSON.

Return ONLY valid JSON.

Do not explain.
Do not add markdown.
Do not add text before or after JSON.

Available Tools:

1. open_app
Description:
Open desktop applications.

Payload:
{{
    "app": "<application name>"
}}

--------------------------------------------------

2. close_app
Description:
Close desktop applications.

Payload:
{{
    "app": "<application name>"
}}

--------------------------------------------------

3. open_website
Description:
Open websites.

Payload:
{{
    "url": "<website url>"
}}

--------------------------------------------------

4. system_info
Description:
Get system information.

Valid types:
- cpu
- ram
- battery

Payload:
{{
    "type": "<cpu|ram|battery>"
}}

--------------------------------------------------

5. file_tool
Description:
File and folder operations.

Actions:
- create_folder
- create_file
- write_file
- read_file
- delete_file
- list_files
- copy_file
- move_file

6. terminal_tool

Description:
Execute safe terminal commands.

Allowed Commands:
- ipconfig
- ping
- dir
- hostname
- whoami
- systeminfo


7. memory_tool

Actions:
- remember
- recall
- forget
- list

8. code_tool

Description:
Generate complete source code files.



Payload examples:

{{
    "action": "create_folder",
    "name": "test"
}}

{{
    "action": "create_file",
    "name": "notes.txt"
}}

{{
    "action": "write_file",
    "name": "notes.txt",
    "content": "hello world"
}}

{{
    "action": "read_file",
    "name": "notes.txt"
}}

{{
    "action": "delete_file",
    "name": "notes.txt"
}}

{{
    "action": "list_files"
}}

{{
    "action": "copy_file",
    "source_name": "test.txt",
    "destination_name": "backup.txt"
}}

{{
    "action": "move_file",
    "source_name": "backup.txt",
    "destination_name": "archive.txt"
}}

--------------------------------------------------

Examples:

User: open chrome

{{
    "tool": "open_app",
    "payload": {{
        "app": "chrome"
    }}
}}

User: launch vscode

{{
    "tool": "open_app",
    "payload": {{
        "app": "vscode"
    }}
}}

User: close chrome

{{
    "tool": "close_app",
    "payload": {{
        "app": "chrome"
    }}
}}

User: terminate notepad

{{
    "tool": "close_app",
    "payload": {{
        "app": "notepad"
    }}
}}

User: open youtube

{{
    "tool": "open_website",
    "payload": {{
        "url": "https://youtube.com"
    }}
}}

User: open github

{{
    "tool": "open_website",
    "payload": {{
        "url": "https://github.com"
    }}
}}

User: show ram usage

{{
    "tool": "system_info",
    "payload": {{
        "type": "ram"
    }}
}}

User: show cpu usage

{{
    "tool": "system_info",
    "payload": {{
        "type": "cpu"
    }}
}}

User: battery status

{{
    "tool": "system_info",
    "payload": {{
        "type": "battery"
    }}
}}

User: create folder named test

{{
    "tool": "file_tool",
    "payload": {{
        "action": "create_folder",
        "name": "test"
    }}
}}

User: create file notes.txt

{{
    "tool": "file_tool",
    "payload": {{
        "action": "create_file",
        "name": "notes.txt"
    }}
}}

User: write hello world to notes.txt

{{
    "tool": "file_tool",
    "payload": {{
        "action": "write_file",
        "name": "notes.txt",
        "content": "hello world"
    }}
}}

User: read notes.txt

{{
    "tool": "file_tool",
    "payload": {{
        "action": "read_file",
        "name": "notes.txt"
    }}
}}

User: delete notes.txt

{{
    "tool": "file_tool",
    "payload": {{
        "action": "delete_file",
        "name": "notes.txt"
    }}
}}

User: list files

{{
    "tool": "file_tool",
    "payload": {{
        "action": "list_files"
    }}
}}

User: copy test.txt to backup.txt

{{
    "tool": "file_tool",
    "payload": {{
        "action": "copy_file",
        "source_name": "test.txt",
        "destination_name": "backup.txt"
    }}
}}

User: duplicate notes.txt as notes_copy.txt

{{
    "tool": "file_tool",
    "payload": {{
        "action": "copy_file",
        "source_name": "notes.txt",
        "destination_name": "notes_copy.txt"
    }}
}}

User: move backup.txt to archive.txt

{{
    "tool": "file_tool",
    "payload": {{
        "action": "move_file",
        "source_name": "backup.txt",
        "destination_name": "archive.txt"
    }}
}}

User: rename notes.txt to report.txt

{{
    "tool": "file_tool",
    "payload": {{
        "action": "move_file",
        "source_name": "notes.txt",
        "destination_name": "report.txt"
    }}
}}

User: show my ip configuration

{{
    "tool": "terminal_tool",
    "payload": {{
        "command": "ipconfig"
    }}
}}

User: who am i

{{
    "tool": "terminal_tool",
    "payload": {{
        "command": "whoami"
    }}
}}

User: show computer name

{{
    "tool": "terminal_tool",
    "payload": {{
        "command": "hostname"
    }}
}}

{{
  "tool": "memory_tool",
  "payload": {{
    "action": "remember",
    "key": "name",
    "value": "Vishnu"
  }}
}}

{{
  "tool": "memory_tool",
  "payload": {{
    "action": "recall",
    "key": "name"
  }}
}}

{{
  "tool": "memory_tool",
  "payload": {{
    "action": "forget",
    "key": "name"
  }}
}}

{{
    "tool": "memory_tool",
    "payload": {{
        "action": "list"
    }}
}}

User: what do you remember about me

{{
    "tool": "memory_tool",
    "payload": {{
        "action": "list"
    }}
}}

User: show all memories

{{
    "tool": "memory_tool",
    "payload": {{
        "action": "list"
    }}
}}

User: list memories

{{
    "tool": "memory_tool",
    "payload": {{
        "action": "list"
    }}
}}


IMPORTANT

If user says:

- open X website
- open X in browser
- open web version of X

Use open_website.

If user says:

- open X app

Use open_app.

If user only says:

- open X

Prefer open_app.



Yep, there it is.

Your file_tool.py confirms exactly what's happening:

elif action == "create_file":

    with open(path, "w", encoding="utf-8") as f:
        pass

That code literally creates an empty file and does nothing else.

So when Ollama returns:

{{
  "tool": "file_tool",
  "payload": {{
    "action": "create_file",
    "name": "hello.py",
    "content": "print('Hello World')"
  }}
}}

the "content" field gets ignored.

That's why:

hello.py

is empty.

The bigger issue though:

Your AI is still choosing:

"tool": "file_tool"

instead of:

"tool": "code_tool"

So even if you fixed create_file, you're not actually testing the new code generator.

Check two places now:

Examples:

User: create a python hello world program

{{
  "tool": "code_tool",
  "payload": {{
      "file_name": "hello.py",
      "prompt": "Create a Python hello world program"
  }}
}}

User: create a calculator app

{{
  "tool": "code_tool",
  "payload": {{
      "file_name": "calculator.py",
      "prompt": "Create a calculator app"
  }}
}}



Command:
{command}
"""

        try:

            response = await self.llm.generate(prompt)

            print("\n====================")
            print("OLLAMA RESPONSE:")
            print(response)
            print("====================\n")

            match = re.search(
                r"\{.*\}",
                response,
                re.DOTALL
            )

            if not match:
                print("NO JSON FOUND")
                return None

            json_text = match.group()

            print("EXTRACTED JSON:")
            print(json_text)

            return json.loads(json_text)

        except Exception as e:

            print("\nAI ROUTER ERROR:")
            print(str(e))

            return None