import os
from typing import List, Optional

class ModuleResolver:
    """
    Resolves import statements to actual local file paths.
    Currently focuses on Python imports.
    """
    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()

    def resolve_python_import(self, target: str, base_file: str) -> Optional[str]:
        """
        Takes a target like '.services' or 'apps.users.models' and a base_file like 'apps/orders/views/web.py'.
        Returns the absolute file path if found locally, otherwise None.
        """
        if not target:
            return None
            
        base_dir = os.path.dirname(os.path.abspath(base_file))
        
        # 1. Handle relative imports (e.g. '.services', '..models')
        if target.startswith('.'):
            dots = 0
            for char in target:
                if char == '.':
                    dots += 1
                else:
                    break
                    
            module_name = target[dots:]
            
            # For each dot beyond the first, we go up one directory
            current_dir = base_dir
            for _ in range(dots - 1):
                current_dir = os.path.dirname(current_dir)
                
            return self._find_file(current_dir, module_name)
            
        # 2. Handle absolute imports (e.g. 'apps.users.models')
        else:
            # We check if it exists in the project root
            return self._find_file(self.project_root, target)

    def _find_file(self, base_dir: str, module_name: str) -> Optional[str]:
        if not module_name:
            # If the import was just '.' or '..', it points to the directory's __init__.py
            init_path = os.path.join(base_dir, "__init__.py")
            if os.path.exists(init_path):
                return init_path
            return None
            
        parts = module_name.split('.')
        
        # Try finding as a .py file (e.g. apps/users/models.py)
        py_path = os.path.join(base_dir, *parts) + ".py"
        if os.path.exists(py_path):
            return py_path
            
        # Try finding as a package (e.g. apps/users/models/__init__.py)
        pkg_path = os.path.join(base_dir, *parts, "__init__.py")
        if os.path.exists(pkg_path):
            return pkg_path
            
        return None
