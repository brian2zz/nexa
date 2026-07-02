import os
import hashlib
from pathlib import Path

def get_global_nexa_dir() -> str:
    """Returns the global .nexa directory in the user's home folder."""
    home_dir = str(Path.home())
    return os.path.join(home_dir, ".nexa")

def get_project_nexa_dir(project_path: str) -> str:
    """
    Returns a specific .nexa directory for the given project path
    by hashing the absolute path to prevent collisions.
    """
    global_dir = get_global_nexa_dir()
    path_hash = hashlib.md5(os.path.abspath(project_path).encode('utf-8')).hexdigest()
    project_dir = os.path.join(global_dir, "projects", path_hash)
    os.makedirs(project_dir, exist_ok=True)
    return project_dir
