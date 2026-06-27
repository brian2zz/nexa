import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from nexa.core.ai.providers import ProviderFactory
from nexa.config import Config

print("Testing mock provider creation...")
Config._store["provider"] = "mock"
mock_provider = ProviderFactory.create()
print("Mock Provider:", mock_provider)
print("Mock Provider Health:", mock_provider.health())
print("Mock models:", mock_provider.list_models())
response = mock_provider.generate([{"role": "user", "content": "analyze"}])
print("Mock generate snippet:", str(response)[:100])

print("\nTesting ollama provider creation...")
Config._store["provider"] = "ollama"
# Ollama models available according to user context: qwen3:14b
Config._store["ollama.model"] = "qwen3:14b"
try:
    ollama_provider = ProviderFactory.create()
    print("Ollama Provider:", ollama_provider)
    print("Ollama Provider Health:", ollama_provider.health())
    print("Ollama models:", ollama_provider.list_models())
    
    response = ollama_provider.generate([{"role": "user", "content": "hello"}])
    print("Ollama generate snippet:", str(response)[:100])
except Exception as e:
    print("Ollama Error (Expected if Ollama is not actually running):", e)
