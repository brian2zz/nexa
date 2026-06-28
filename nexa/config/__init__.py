import os
import json
from pathlib import Path

class Config:
    _store = {}
    _config_file = Path.home() / ".nexa" / "config.json"

    @classmethod
    def load(cls):
        if not cls._store:
            # Default values
            cls._store = {
                "provider": "ollama",
                "ollama.host": "http://localhost:11434",
                "ollama.model": "qwen3:14b",
                "ollama.temperature": 0.2,
                "deepseek.model": "deepseek-chat",
                "groq.model": "llama-3.1-8b-instant",
                "gemini.model": "gemini-2.5-flash"
            }
            if cls._config_file.exists():
                try:
                    with open(cls._config_file, "r") as f:
                        data = json.load(f)
                        cls._store.update(data)
                except Exception:
                    pass

    @classmethod
    def save(cls):
        cls._config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cls._config_file, "w") as f:
            json.dump(cls._store, f, indent=4)

    @classmethod
    def get(cls, key: str, default=None):
        cls.load()
        return cls._store.get(key, default)
        
    @classmethod
    def set(cls, key: str, value):
        cls.load()
        cls._store[key] = value
        cls.save()

# Auto-load on import
Config.load()
