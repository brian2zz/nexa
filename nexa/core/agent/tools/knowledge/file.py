import os
import json
from nexa.core.agent.indexer import WorkspaceIndexer
from nexa.core.ai.knowledge.summarizer import RegexSummarizer
from nexa.core.ai.knowledge.dependency import DependencyParser
class FileTool:
    """
    Domain-specific tool for interacting with Files (Read-Only).
    """
    def __init__(self, workspace_path: str, cache=None):
        self.workspace_path = workspace_path
        self.indexer = WorkspaceIndexer(workspace_path)
        # Scan on init since we don't have a startup hook yet
        self.indexer.scan_workspace(async_scan=True)
        if cache:
            self.cache = cache
        else:
            from nexa.core.ai.knowledge.cache.sqlite import SQLiteCache
            db_path = os.path.join(workspace_path, ".nexa_cache.db")
            self.cache = SQLiteCache(db_path=db_path)
        self.summarizer = RegexSummarizer(cache=self.cache)
        self.dependency_parser = DependencyParser(cache=self.cache)

    def find(self, extension: str = None, name: str = None) -> str:
        """
        Queries the WorkspaceIndexer to find files quickly without disk walking.
        """
        self.indexer.wait_for_scan()
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

    def read_symbol(self, symbol_name: str) -> str:
        """
        Phase 5: Read a specific symbol (function, class) from AST Index.
        Returns a rich semantic JSON object containing the exact lines of code.
        """
        self.indexer.wait_for_scan()
        results = self.indexer.query_symbols(symbol_name)
        if not results:
            return f"Symbol '{symbol_name}' not found in any parsed files."
            
        semantic_objects = []
        for res in results:
            filepath = res["filepath"]
            start_line = res["start_line"]
            end_line = res["end_line"]
            
            full_path = os.path.join(self.workspace_path, filepath) if not os.path.isabs(filepath) else filepath
            
            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
                    
                # line numbers are 1-indexed in ast
                start_idx = max(0, start_line - 1)
                end_idx = min(len(lines), end_line)
                
                code_block = "".join(lines[start_idx:end_idx])
                
                # C.1: Enhance with summary and dependencies
                ext = os.path.splitext(filepath)[1].lower()
                lang = "python" if ext == ".py" else ("php" if ext == ".php" else ("javascript" if ext in [".js", ".jsx", ".ts", ".tsx"] else "unknown"))
                
                summary_obj = self.summarizer.summarize(code_block, lang, filepath)
                deps = self.dependency_parser.parse(code_block, lang, filepath)
                call_graph = self.indexer.query_call_graph(res["name"])
                
                semantic_objects.append({
                    "type": res["type"],
                    "name": res["name"],
                    "file": filepath,
                    "lines": [start_line, end_line],
                    "code": code_block,
                    "summary": summary_obj.__dict__ if hasattr(summary_obj, "__dict__") else summary_obj,
                    "dependencies": [d[0] for d in deps],
                    "callers": call_graph["callers"],
                    "callees": call_graph["callees"]
                })
            except Exception as e:
                pass
                
        return json.dumps(semantic_objects, indent=2)

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
