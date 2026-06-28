from typing import Dict, Type
from .providers import BaseContextProvider, GitContextProvider, ProjectContextProvider, LogContextProvider

class ContextProviderRegistry:
    """Registry that maps Intents to Context Providers."""
    def __init__(self):
        self.providers: Dict[str, BaseContextProvider] = {}
        self._register_defaults()
        
    def _register_defaults(self):
        self.register("COMMIT", GitContextProvider())
        self.register("REFACTOR", ProjectContextProvider())
        self.register("BUGFIX", LogContextProvider())
        # Default PLAN generic provider could just be empty or base project info
        
    def register(self, intent: str, provider: BaseContextProvider):
        self.providers[intent.upper()] = provider
        
    def resolve(self, intent: str, cwd: str) -> str:
        """Returns the context string for the given intent, or empty string if not found."""
        intent = intent.upper()
        
        # Exact match
        if intent in self.providers:
            return self.providers[intent].provide(cwd)
            
        # Fuzzy match for PLAN sub-intents (e.g. if Intent Classifier returns "PLAN COMMIT")
        for key, provider in self.providers.items():
            if key in intent:
                return provider.provide(cwd)
                
        return ""
