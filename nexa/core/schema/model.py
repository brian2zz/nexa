from dataclasses import dataclass, field
from .field import FieldSchema

@dataclass
class ModelSchema:
    name: str
    app: str
    fields: list[FieldSchema] = field(default_factory=list)
    crud: dict = field(default_factory=lambda: {"enabled": True})