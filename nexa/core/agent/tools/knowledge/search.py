import os
import subprocess
import shutil

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
            # 1. Try rg (ripgrep)
            if shutil.which("rg"):
                result = subprocess.run(
                    ['rg', '-n', '-i', query, full_path],
                    capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=15
                )
                if result.stdout:
                    return self._truncate(result.stdout)
                
            # 2. Try grep
            if shutil.which("grep"):
                result = subprocess.run(
                    ['grep', '-rn', '-i', query, full_path],
                    capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=15
                )
                if result.stdout:
                    return self._truncate(result.stdout)
                    
            # 3. Fallback Python murni
            matches = []
            ignore_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.env', '.venv', '.pytest_cache'}
            
            for root, dirs, files in os.walk(full_path):
                dirs[:] = [d for d in dirs if d not in ignore_dirs]
                for file in files:
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                            for i, line in enumerate(f, 1):
                                if query.lower() in line.lower():
                                    rel_path = os.path.relpath(filepath, self.workspace_path)
                                    matches.append(f"{rel_path}:{i}:{line.rstrip()}")
                                    if len(matches) >= 50:
                                        matches.append("... (TRUNCATED)")
                                        return "\n".join(matches)
                    except Exception:
                        pass
                        
            if matches:
                return "\n".join(matches)
                
            return "No matches found."
        except Exception as e:
            return f"Error searching text: {e}"

    def _truncate(self, text: str, max_lines: int = 50) -> str:
        lines = text.split('\n')
        if len(lines) > max_lines:
            return "\n".join(lines[:max_lines]) + "\n... (TRUNCATED)"
        return text

    def symbol(self, name: str, language: str = "python") -> str:
        """
        Searches for a symbol (class, function, variable) definition.
        """
        # Placeholder for more advanced AST-based or regex-based symbol search
        # For now, falls back to text search with heuristics
        heuristics = f"class {name}" if language == "python" else f"function {name}"
        return self.text(heuristics)
