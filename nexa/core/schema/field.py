from dataclasses import dataclass, field

class NexaValidationError(Exception):
    pass

@dataclass
class FieldSchema:
    name: str
    type: str
    required: bool = True
    to: str = None              # Format: "app.Model" or "Model"
    on_delete: str = "CASCADE"
    extra: dict = field(default_factory=dict)