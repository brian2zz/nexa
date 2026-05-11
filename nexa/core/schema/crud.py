from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class TableSchema:
    searchable: List[str] = field(default_factory=list)
    sortable: List[str] = field(default_factory=list)
    columns: List[str] = field(default_factory=list) # Visioner: explicit column selection

@dataclass
class FormSchema:
    layout: str = "default" # "default", "tabs", "sections"
    fields: List[str] = field(default_factory=list)

@dataclass
class CrudSchema:
    enabled: bool = True
    table: TableSchema = field(default_factory=TableSchema)
    form: FormSchema = field(default_factory=FormSchema)
    # Visionary: Permissions or meta info
    meta: dict = field(default_factory=dict)
