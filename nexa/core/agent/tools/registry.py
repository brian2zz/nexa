from typing import Dict, Any, Callable, Optional
from nexa.core.agent.tools.models import ToolMetadata

class ToolRegistry:
    """
    Penyimpanan sentral untuk semua Tool yang diizinkan untuk LLM.
    Memastikan LLM hanya dapat mengakses alat yang telah diregistrasi.
    """
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: Dict[str, dict] = {}
        self._metadata: Dict[str, ToolMetadata] = {}
        
    def register(self, name: str, func: Callable, schema: dict, metadata: Optional[ToolMetadata] = None):
        """
        Mendaftarkan Tool, schema JSON-nya, dan metadata untuk ToolPrioritizer.
        """
        self._tools[name] = func
        self._schemas[name] = schema
        if metadata:
            self._metadata[name] = metadata
        else:
            # Default metadata if not provided
            self._metadata[name] = ToolMetadata(
                name=name, cost=10, latency="medium", category="general", read_only=False, priority=50
            )
        
    def get_all_schemas(self) -> list:
        return list(self._schemas.values())

    def get_metadata(self, name: str) -> Optional[ToolMetadata]:
        return self._metadata.get(name)

    def get_all_metadata(self) -> Dict[str, ToolMetadata]:
        return self._metadata
        
    def execute(self, name: str, kwargs: dict) -> Any:
        if name not in self._tools:
            return f"Error: Tool '{name}' is not permitted or does not exist."
        
        try:
            return self._tools[name](**kwargs)
        except Exception as e:
            return f"Error executing '{name}': {str(e)}"
