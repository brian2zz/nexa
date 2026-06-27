from typing import Dict, Type
from .base import LLMProvider
from nexa.config import Config

class ProviderFactory:
    _registry: Dict[str, Type[LLMProvider]] = {}

    @classmethod
    def register(cls, name: str, provider_class: Type[LLMProvider]):
        """Register a new LLM provider class."""
        cls._registry[name.lower()] = provider_class

    @classmethod
    def create(cls) -> LLMProvider:
        """
        Create and return an instance of the configured LLM provider.
        Reads the 'provider' key from configuration.
        """
        provider_name = Config.get("provider", "mock").lower()
        
        if provider_name not in cls._registry:
            raise ValueError(f"Provider '{provider_name}' is not registered in ProviderFactory.")
            
        provider_class = cls._registry[provider_name]
        return provider_class()
