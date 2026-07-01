from typing import Any

class TerminalRunner:
    def execute(self, command: str, **kwargs) -> Any:
        # Guard clause: reject 'cd' command before parsing
        stripped_command = command.strip()
        if stripped_command.startswith("cd "):
            raise ValueError("The 'cd' command is not allowed in this runner.")
        # Existing parsing and execution logic below
        # ...