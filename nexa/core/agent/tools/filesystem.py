import os
from typing import List, Dict, Any

class FilesystemTool:
    """
    Provides the agent with advanced write and edit capabilities.
    """
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path

    def _resolve_path(self, path: str) -> str:
        # Ensure path is within workspace
        abs_path = os.path.abspath(os.path.join(self.workspace_path, path))
        if not abs_path.startswith(os.path.abspath(self.workspace_path)):
            raise ValueError(f"Path {path} is outside the workspace directory.")
        return abs_path

    def list_directory(self, path: str = ".") -> str:
        """
        Lists files and directories in the given path.
        """
        try:
            target_dir = self._resolve_path(path)
            if not os.path.isdir(target_dir):
                return f"Error: '{path}' is not a valid directory."
                
            items = os.listdir(target_dir)
            files = []
            dirs = []
            for item in items:
                item_path = os.path.join(target_dir, item)
                if os.path.isdir(item_path):
                    dirs.append(f"[DIR]  {item}/")
                else:
                    files.append(f"[FILE] {item}")
                    
            dirs.sort()
            files.sort()
            
            result = f"Contents of {path}:\n"
            result += "\n".join(dirs + files)
            if not items:
                result += "(Empty directory)"
            return result
            
        except Exception as e:
            return f"Error listing directory: {str(e)}"

    def write_file(self, filepath: str, content: str) -> str:
        """
        Creates a new file or completely overwrites an existing file.
        """
        try:
            target_file = self._resolve_path(filepath)
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return f"Successfully wrote {len(content)} characters to {filepath}."
        except Exception as e:
            return f"Error writing to file {filepath}: {str(e)}"

    def edit_file_content(self, filepath: str, search_block: str, replace_block: str) -> str:
        """
        Replaces an exact match of 'search_block' with 'replace_block' in the specified file.
        """
        try:
            target_file = self._resolve_path(filepath)
            if not os.path.exists(target_file):
                return f"Error: File {filepath} does not exist."
                
            with open(target_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if search_block not in content:
                # Try normalizing line endings in case of CRLF vs LF issues
                content_normalized = content.replace("\r\n", "\n")
                search_normalized = search_block.replace("\r\n", "\n")
                
                if search_normalized not in content_normalized:
                    return f"Error: The exact search block was not found in {filepath}. Ensure whitespace and indentation match exactly."
                    
                content = content_normalized
                search_block = search_normalized
                
            # Count occurrences
            occurrences = content.count(search_block)
            if occurrences > 1:
                return f"Error: The search block was found {occurrences} times in {filepath}. The search block must be unique."
                
            new_content = content.replace(search_block, replace_block)
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            return f"Successfully replaced content in {filepath}."
        except Exception as e:
            return f"Error editing file {filepath}: {str(e)}"
