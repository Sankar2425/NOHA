BLOCKED_COMMANDS = [
    "del",
    "erase",
    "rmdir",
    "format",
    "shutdown",
    "restart",
    "taskkill",
    "diskpart",
    "reg",
    "powershell",
    "curl",
    "wget",
    "net user",
    "net localgroup",
    "sc delete"
]

ALLOWED_COMMANDS = [
    "ipconfig",
    "ping",
    "dir",
    "hostname",
    "whoami",
    "systeminfo"
]

class CommandGuard:

    @staticmethod
    def validate(command: str):

        command = command.lower().strip()

        for blocked in BLOCKED_COMMANDS:

            if blocked in command:

                return False

        return True
    
    @staticmethod
    def is_allowed_terminal_command(command: str):

        command = command.lower().strip()

        for allowed in ALLOWED_COMMANDS:

            if command.startswith(allowed):
                return True

        return False