from dataclasses import dataclass
from typing import Optional
from nexa.core.models.enums import Status

@dataclass
class ApprovalResult:
    """
    DTO yang merepresentasikan keputusan Approval.
    Dikembalikan oleh ApprovalEngine ke ExecutionEngine.
    """
    is_approved: bool
    status: Status
    approver_id: str  # e.g., "TelegramUser-123", "CLI-Admin"
    reason: Optional[str] = None  # Alasan spesifik jika ditolak (misal dari Critic AI)
    timeout_occurred: bool = False
