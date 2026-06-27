import json
from typing import List, Dict, Any

class PromptFormatter:
    def __init__(self):
        self.parts = []
        self.separator = "=================================="

    def add_section(self, title: str):
        self.parts.append(self.separator)
        self.parts.append(title.upper())
        self.parts.append(self.separator)

    def add_text(self, text: str):
        if text.strip():
            self.parts.append(text.strip())

    def add_list(self, items: List[str]):
        for item in items:
            self.parts.append(f"- {item}")

    def add_table(self, data: Dict[str, Any]):
        for key, value in data.items():
            self.parts.append(f"{key}: {value}")

    def add_code(self, code: str, language: str = ""):
        self.parts.append(f"```{language}")
        self.parts.append(code.strip())
        self.parts.append("```")

    def add_warning(self, warnings: List[str]):
        if warnings:
            self.parts.append("WARNINGS:")
            for w in warnings:
                self.parts.append(f"!! {w}")

    def add_json(self, data: Any):
        self.parts.append("```json")
        self.parts.append(json.dumps(data, indent=2))
        self.parts.append("```")

    def build(self) -> str:
        return "\n\n".join(self.parts)
