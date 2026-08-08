import subprocess
import shlex
from typing import Dict, Any

class GitTool:
    """Read-only tool for extracting Git knowledge."""
    
    def __init__(self, cwd: str):
        self.cwd = cwd

    def status(self) -> str:
        """Returns the output of git status."""
        try:
            result = subprocess.run(
                ["git", "status"],
                cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace'
            )
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return f"Git Error: {e}"

    def diff(self) -> str:
        """Returns the output of git diff (staged and unstaged)."""
        try:
            # Unstaged changes
            result = subprocess.run(
                ["git", "diff"],
                cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace'
            )
            unstaged = result.stdout
            
            # Staged changes
            result_staged = subprocess.run(
                ["git", "diff", "--cached"],
                cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace'
            )
            staged = result_staged.stdout
            
            output = ""
            if staged:
                output += "--- STAGED CHANGES ---\n" + staged + "\n"
            if unstaged:
                output += "--- UNSTAGED CHANGES ---\n" + unstaged + "\n"
                
            if not output:
                return "No changes detected."
                
            # Truncate output if it's too large to prevent LLM payload overflow (e.g. max 12000 chars)
            max_chars = 12000
            if len(output) > max_chars:
                output = output[:max_chars] + f"\n\n... [TRUNCATED] Diff is too large ({len(output)} chars). Showing first {max_chars} chars."
                
            return output
        except Exception as e:
            return f"Git Error: {e}"

    def current_branch(self) -> str:
        """Returns the current git branch."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace'
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "No Git Repository"
        except Exception:
            return "Git not installed or not found"

    def log(self, limit: int = 10) -> str:
        """Returns the recent git commit history."""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", f"-{limit}"],
                cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace'
            )
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return f"Git Error: {e}"

    def execute(self, command: str) -> str:
        """Executes any git command and returns the output."""
        try:
            try:
                args = shlex.split(command)
            except ValueError:
                return "Error: Could not parse command."
                
            if not args or args[0] != "git":
                return "Error: Only git commands are allowed."
                
            allowed_subcommands = {
                "status", "diff", "log", "blame", "branch", "rev-parse",
                "show", "remote", "tag", "stash", "ls-files"
            }
            
            if len(args) < 2 or args[1] not in allowed_subcommands:
                return "Error: Command not in allowed list."
            
            result = subprocess.run(
                args,
                cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace', shell=False
            )
            output = result.stdout if result.returncode == 0 else result.stderr
            if not output:
                return f"Command '{command}' executed successfully with no output."
                
            max_chars = 12000
            if len(output) > max_chars:
                output = output[:max_chars] + f"\n\n... [TRUNCATED] Output is too large ({len(output)} chars)."
            return output
        except Exception as e:
            return f"Git Error: {e}"

def git_status(cwd: str) -> str:
    return GitTool(cwd).status()

def git_diff(cwd: str) -> str:
    return GitTool(cwd).diff()

def git_execute(cwd: str, command: str) -> str:
    return GitTool(cwd).execute(command)

def git_current_branch(cwd: str) -> str:
    return GitTool(cwd).current_branch()

def git_log(cwd: str, limit: int = 10) -> str:
    return GitTool(cwd).log(limit)

GIT_STATUS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "git_status",
        "description": "Get the current git status (modified files, untracked files).",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

GIT_DIFF_SCHEMA = {
    "type": "function",
    "function": {
        "name": "git_diff",
        "description": "Get the current git diff to see exact line changes.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

GIT_EXECUTE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "git_execute",
        "description": "Execute any git command (e.g. 'git log', 'git blame file.py', 'git branch') and get the output.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The full git command to execute, must start with 'git'."
                }
            },
            "required": ["command"]
        }
    }
}

GIT_CURRENT_BRANCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "git_current_branch",
        "description": "Get the current git branch name.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

GIT_LOG_SCHEMA = {
    "type": "function",
    "function": {
        "name": "git_log",
        "description": "Get recent git commits history.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of commits to return."
                }
            },
            "required": []
        }
    }
}

def register_git_tools(registry, cwd: str):
    registry.register("git_status", lambda: git_status(cwd), GIT_STATUS_SCHEMA)
    registry.register("git_diff", lambda: git_diff(cwd), GIT_DIFF_SCHEMA)
    registry.register("git_execute", lambda command: git_execute(cwd, command), GIT_EXECUTE_SCHEMA)
    registry.register("git_current_branch", lambda: git_current_branch(cwd), GIT_CURRENT_BRANCH_SCHEMA)
    registry.register("git_log", lambda limit=10: git_log(cwd, limit), GIT_LOG_SCHEMA)
