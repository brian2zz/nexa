import os

class FileScanner:
    def scan(self, root_path="."):
        from ..config import AgentConfig
        ignore_list = AgentConfig.IGNORE_LIST
        
        scanned_files = []
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Ignore directories
            dirnames[:] = [d for d in dirnames if d not in ignore_list and not d.startswith('.')]
            
            for file in filenames:
                file_path = os.path.join(dirpath, file)
                rel_path = os.path.relpath(file_path, root_path)
                
                # Normalize slashes for consistency
                rel_path = rel_path.replace("\\", "/")
                
                _, ext = os.path.splitext(file)
                try:
                    size = os.path.getsize(file_path)
                except Exception:
                    size = 0
                    
                scanned_files.append({
                    "path": rel_path,
                    "extension": ext.lstrip('.'),
                    "size": size
                })
                
        return scanned_files
