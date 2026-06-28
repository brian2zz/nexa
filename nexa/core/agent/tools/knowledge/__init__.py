import os

def read_file(filepath: str) -> str:
    """Membaca isi file (Read-Only)."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def list_directory(path: str = ".") -> str:
    """Melihat isi direktori (Read-Only)."""
    try:
        return "\n".join(os.listdir(path))
    except Exception as e:
        return f"Error listing directory: {e}"

def search_code(query: str, path: str = ".") -> str:
    """Mencari string/pattern dalam file-file di direktori."""
    import subprocess
    try:
        result = subprocess.run(
            ['findstr', '/S', '/I', '/N', '/C:' + query, os.path.join(path, '*.*')],
            capture_output=True, text=True, timeout=15
        )
        if result.stdout:
            # Batasi output agar tidak menghabiskan token
            lines = result.stdout.split('\n')
            if len(lines) > 50:
                return "\n".join(lines[:50]) + "\n... (TRUNCATED)"
            return result.stdout
        return "No matches found."
    except Exception as e:
        return f"Error searching code: {e}"

# Schemas for LLM
READ_FILE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the contents of a file. Use this to understand the code.",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Absolute or relative path to the file"}
            },
            "required": ["filepath"]
        }
    }
}

LIST_DIR_SCHEMA = {
    "type": "function",
    "function": {
        "name": "list_directory",
        "description": "List all files and folders in a directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the directory"}
            },
            "required": ["path"]
        }
    }
}

SEARCH_CODE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_code",
        "description": "Search for a specific string, function name, or variable across all files in the project. Use this to find where things are defined or used.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The string or pattern to search for"},
                "path": {"type": "string", "description": "Directory to search in (default is current directory '.')"}
            },
            "required": ["query"]
        }
    }
}

def register_knowledge_tools(registry, cwd: str = None):
    registry.register("read_file", read_file, READ_FILE_SCHEMA)
    registry.register("list_directory", list_directory, LIST_DIR_SCHEMA)
    registry.register("search_code", search_code, SEARCH_CODE_SCHEMA)
    
    # Register Git tools if cwd is provided
    if cwd:
        from .git import register_git_tools
        register_git_tools(registry, cwd)
