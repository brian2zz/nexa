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
    related_name: str = None # NEW: Support for custom related names
    extra: dict = field(default_factory=dict)