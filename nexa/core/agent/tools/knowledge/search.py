import os
import subprocess

class SearchTool:
    """
    Domain-specific tool for searching content inside files (Read-Only).
    """
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path

    def text(self, query: str, path: str = ".") -> str:
        """
        Searches for a text query across the project.
        """
        full_path = os.path.join(self.workspace_path, path) if not os.path.isabs(path) else path
        try:
            result = subprocess.run(
                ['findstr', '/S', '/I', '/N', '/C:' + query, os.path.join(full_path, '*.*')],
                capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=15
            )
            if result.stdout:
                lines = result.stdout.split('\n')
                if len(lines) > 50:
                    return "\n".join(lines[:50]) + "\n... (TRUNCATED)"
                return result.stdout
            return "No matches found."
        except Exception as e:
            return f"Error searching text: {e}"

    def symbol(self, name: str, language: str = "python") -> str:
        """
        Searches for a symbol (class, function, variable) definition.
        """
        # Placeholder for more advanced AST-based or regex-based symbol search
        # For now, falls back to text search with heuristics
        heuristics = f"class {name}" if language == "python" else f"function {name}"
        return self.text(heuristics)
