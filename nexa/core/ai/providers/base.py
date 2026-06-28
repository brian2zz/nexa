from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.2, tools: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a response from the LLM based on a list of messages.
        
        Expected messages format:
        [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."}
        ]
        
        Returns a dictionary with metadata:
        {
            "content": "...",
            "provider": "...",
            "model": "...",
            "tool_calls": [...],
            "usage": {}
        }
        """
        pass

    @abstractmethod
    def health(self) -> bool:
        """
        Check if the provider service is accessible.
        Returns True if healthy, False otherwise.
        """
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """
        List all available models for this provider.
        """
        pass
