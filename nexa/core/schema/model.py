from dataclasses import dataclass, field
from .field import FieldSchema
from nexa.core.schema.crud import CrudSchema

@dataclass
class ModelSchema:
    name: str
    app: str
    fields: list[FieldSchema] = field(default_factory=list)
    crud: CrudSchema = field(default_factory=CrudSchema)