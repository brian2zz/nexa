from dataclasses import dataclass, field
from .model import ModelSchema

@dataclass
class AppSchema:
    name: str
    models: list[ModelSchema] = field(default_factory=list)