class WorkspaceRule:
    """
    Rule to validate that a given file path is within the workspace root directory.
    Removes the '/d' flag if present before checking for directory traversal.
    Raises explicit errors for absolute paths and traversal attempts.
    """

    def __init__(self, workspace_root: str):
        """
        Initialize with the workspace root directory.
        """
        self.workspace_root = workspace_root

    def validate(self, path: str) -> str:
        """
        Validate and resolve a path relative to the workspace root.
        Returns the normalized absolute path if valid, raises ValueError otherwise.
        """
        # Filter out the '/d' flag prefix (e.g., "/d path/to/file" or "/d/path/to/file")
        if path.startswith('/d '):
            path = path[3:]  # Remove "/d "
        elif path.startswith('/d/'):
            path = path[3:]  # Remove "/d"
        elif path == '/d':
            path = ''  # Single flag without path

        # Reject absolute paths explicitly
        if path.startswith('/') or (len(path) > 1 and path[1] == ':'):
            raise ValueError(f"Absolute path is not allowed: '{path}'")

        import os
        # Normalize the user path
        normalized_path = os.path.normpath(os.path.join(self.workspace_root, path))

        # Ensure the resolved path is within the workspace root
        if not normalized_path.startswith(os.path.abspath(self.workspace_root)):
            raise ValueError(f"Path traversal detected: '{path}' resolves outside workspace")

        return normalized_path