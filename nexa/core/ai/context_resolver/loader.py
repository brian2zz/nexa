import os

class SourceLoader:
    """
    Loads only the source files that are explicitly requested.
    """
    def load(self, project_path: str, file_path: str) -> str:
        full_path = os.path.join(project_path, file_path)
        if not os.path.exists(full_path):
            return ""
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ""
