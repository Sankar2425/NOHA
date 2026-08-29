class IntentRouter:

    async def route(self, command: str):

        command = command.lower().strip()

        # OPEN APPLICATIONS

        if command.startswith("open"):

            words = command.split()

            if len(words) >= 2:

                app_name = " ".join(words[1:])

                return {
                    "tool": "open_app",
                    "payload": {
                        "app": app_name
                    }
                }

        

        if "cpu" in command:

            return {
                "tool": "system_info",
                "payload": {
                    "type": "cpu"
                }
            }

        

        if "ram" in command or "memory" in command:

            return {
                "tool": "system_info",
                "payload": {
                    "type": "ram"
                }
            }

       
        if "battery" in command:

            return {
                "tool": "system_info",
                "payload": {
                    "type": "battery"
                }
            }

        

        return None