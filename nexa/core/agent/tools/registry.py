from typing import Dict, Any, Callable

class ToolRegistry:
    """
    Penyimpanan sentral untuk semua Tool yang diizinkan untuk LLM.
    Memastikan LLM hanya dapat mengakses alat yang telah diregistrasi.
    """
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: Dict[str, dict] = {}
        
    def register(self, name: str, func: Callable, schema: dict):
        """
        Mendaftarkan Tool dan schema JSON-nya (untuk LLM Function Calling).
        """
        self._tools[name] = func
        self._schemas[name] = schema
        
    def get_all_schemas(self) -> list:
        return list(self._schemas.values())
        
    def execute(self, name: str, kwargs: dict) -> Any:
        if name not in self._tools:
            return f"Error: Tool '{name}' is not permitted or does not exist."
        
        try:
            return self._tools[name](**kwargs)
        except Exception as e:
            return f"Error executing '{name}': {str(e)}"
