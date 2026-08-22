import os
import sys
import hashlib
from pathlib import Path

def get_global_nexa_dir() -> str:
    """
    Returns the standard global Nexa AppData directory (like OpenCode/Antigravity):
    - Windows: %APPDATA%/nexa (e.g. C:\\Users\\<User>\\AppData\\Roaming\\nexa)
    - macOS/Linux: ~/.nexa
    """
    if sys.platform == "win32":
        app_data = os.getenv("APPDATA") or os.getenv("LOCALAPPDATA")
        if app_data:
            path = os.path.join(app_data, "nexa")
            os.makedirs(path, exist_ok=True)
            return path

    home_dir = str(Path.home())
    path = os.path.join(home_dir, ".nexa")
    os.makedirs(path, exist_ok=True)
    return path

def get_project_nexa_dir(project_path: str) -> str:
    """
    Returns a specific persistent .nexa directory for the given project path
    by hashing the absolute path to prevent collisions.
    Stored in %APPDATA%/nexa/projects/<hash>/
    """
    global_dir = get_global_nexa_dir()
    path_hash = hashlib.md5(os.path.abspath(project_path).encode('utf-8')).hexdigest()
    project_dir = os.path.join(global_dir, "projects", path_hash)
    os.makedirs(project_dir, exist_ok=True)
    return project_dir
