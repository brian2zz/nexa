import os
import json
from nexa.core.agent.indexer import WorkspaceIndexer

class FileTool:
    """
    Domain-specific tool for interacting with Files (Read-Only).
    """
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.indexer = WorkspaceIndexer(workspace_path)
        # Scan on init since we don't have a startup hook yet
        self.indexer.scan_workspace(async_scan=True)

    def find(self, extension: str = None, name: str = None) -> str:
        """
        Queries the WorkspaceIndexer to find files quickly without disk walking.
        """
        print(f"       [Debug] file_lookup called with extension={extension}, name={name}")
        results = self.indexer.query_files(extension=extension, name=name)
        if not results:
            return "No files found matching the criteria."
        return json.dumps(results, indent=2)

    def read(self, filepath: str) -> str:
        """
        Reads the content of a file.
        """
        full_path = os.path.join(self.workspace_path, filepath) if not os.path.isabs(filepath) else filepath
        try:
            with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def exists(self, filepath: str) -> str:
        full_path = os.path.join(self.workspace_path, filepath) if not os.path.isabs(filepath) else filepath
        return "True" if os.path.exists(full_path) else "False"

    def tree(self, path: str = ".") -> str:
        """
        Returns a flat directory listing for now (could be expanded to a true tree).
        """
        full_path = os.path.join(self.workspace_path, path) if not os.path.isabs(path) else path
        try:
            return "\n".join(os.listdir(full_path))
        except Exception as e:
            return f"Error listing directory: {e}"

    def metadata(self, filepath: str) -> str:
        """
        Returns file metadata (size, modified time).
        """
        full_path = os.path.join(self.workspace_path, filepath) if not os.path.isabs(filepath) else filepath
        try:
            stat = os.stat(full_path)
            return json.dumps({
                "size_bytes": stat.st_size,
                "last_modified": stat.st_mtime
            }, indent=2)
        except Exception as e:
            return f"Error getting metadata: {e}"
