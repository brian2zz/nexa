from dataclasses import dataclass, field
from .app import AppSchema

@dataclass
class ProjectSchema:
    name: str
    version: str = "1"
    apps: list[AppSchema] = field(default_factory=list)