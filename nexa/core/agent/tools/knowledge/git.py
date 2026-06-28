import subprocess
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

def git_status(cwd: str) -> str:
    return GitTool(cwd).status()

def git_diff(cwd: str) -> str:
    return GitTool(cwd).diff()

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

def register_git_tools(registry, cwd: str):
    registry.register("git_status", lambda: git_status(cwd), GIT_STATUS_SCHEMA)
    registry.register("git_diff", lambda: git_diff(cwd), GIT_DIFF_SCHEMA)
