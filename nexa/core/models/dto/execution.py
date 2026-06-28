from dataclasses import dataclass, field
from typing import List, Dict, Optional
from nexa.core.models.enums import Status

@dataclass
class ExecutionResult:
    """
    DTO hasil eksekusi akhir filesystem.
    """
    success: bool
    status: Status
    files_modified: int
    summary: str
    error_message: Optional[str] = None
    failed_files: List[str] = field(default_factory=list)
    rollback_occurred: bool = False
