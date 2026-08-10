import os
import subprocess
import time
from typing import Dict, Any

class TerminalTool:
    """
    Provides the agent with the ability to execute bash/terminal commands.
    """
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path

    def run_bash_command(self, command: str, timeout: int = 60) -> str:
        """
        Executes a terminal command in the workspace directory.
        Returns stdout and stderr as a combined string.
        """
        start_time = time.time()
        try:
            # We use shell=True here because LLM often generates complex commands
            # with pipes, redirects, or environment variable exports.
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.workspace_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout
            )
            
            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
                
            if not output:
                output = f"Command executed successfully with no output. Exit code: {result.returncode}"
                
            duration = time.time() - start_time
            return f"Execution Result (Code: {result.returncode}, Time: {duration:.2f}s):\n{output}"
            
        except subprocess.TimeoutExpired as e:
            output = e.stdout.decode('utf-8', 'replace') if e.stdout else ""
            err = e.stderr.decode('utf-8', 'replace') if e.stderr else ""
            return f"Error: Command timed out after {timeout} seconds.\nSTDOUT: {output}\nSTDERR: {err}"
        except Exception as e:
            return f"System Error executing command: {str(e)}"
