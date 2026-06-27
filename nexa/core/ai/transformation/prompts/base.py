from abc import ABC, abstractmethod
from typing import Dict, Any

class BasePromptBuilder(ABC):
    @abstractmethod
    def build_system_prompt(self, request) -> str:
        pass
        
    @abstractmethod
    def build_user_prompt(self, request) -> str:
        pass

    def build_context_block(self, context_bundle: Dict[str, Any]) -> str:
        """Helper to format the context bundle into string."""
        if not context_bundle or not context_bundle.get("snippets"):
            return ""
            
        block = "### GIVEN CONTEXT:\n"
        for snippet in context_bundle.get("snippets", []):
            block += f"{snippet}\n"
        return block
