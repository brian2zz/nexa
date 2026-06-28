from dataclasses import dataclass, field
from typing import List, Dict, Optional
from nexa.core.models.enums import Status

@dataclass
class VerificationResult:
    """
    DTO hasil proses Verifikasi (Sprint 5).
    """
    success: bool
    status: Status
    syntax_passed: bool = False
    tests_passed: bool = False
    lint_passed: bool = False
    error_messages: List[str] = field(default_factory=list)
    summary: str = ""
