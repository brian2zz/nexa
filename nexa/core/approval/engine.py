import time
import datetime
import threading
from typing import Optional
from nexa.core.events.bus import PipelineBus
from nexa.core.models.events import EventContext
from nexa.core.models.enums import EventPriority, Status
from nexa.core.models.dto.patch import PatchResult
from nexa.core.models.dto.approval import ApprovalResult

class ApprovalEngine:
    """
    Gatekeeper Pipeline. Menghentikan sementara eksekusi dan menunggu 
    Approval dari pihak eksternal (via PipelineBus).
    """
    def __init__(self, bus: PipelineBus):
        self.bus = bus
        # Dictionary untuk menyimpan Event flag per correlation_id
        self._waiting_events = {}
        self._approval_results = {}
        
        # Subscribe untuk menangkap balasan
        self.bus.subscribe("ApprovalGranted", self._on_approval_granted)
        self.bus.subscribe("ApprovalRejected", self._on_approval_rejected)

    def _on_approval_granted(self, context: EventContext) -> None:
        cid = context.correlation_id
        if cid in self._waiting_events:
            payload = context.payload if isinstance(context.payload, dict) else {}
            self._approval_results[cid] = ApprovalResult(
                is_approved=True,
                status=Status.SUCCESS,
                approver_id=payload.get("approver_id", "Unknown"),
                reason=payload.get("reason", "")
            )
            self._waiting_events[cid].set() # Unblock

    def _on_approval_rejected(self, context: EventContext) -> None:
        cid = context.correlation_id
        if cid in self._waiting_events:
            payload = context.payload if isinstance(context.payload, dict) else {}
            self._approval_results[cid] = ApprovalResult(
                is_approved=False,
                status=Status.FAILED,
                approver_id=payload.get("approver_id", "Unknown"),
                reason=payload.get("reason", "Rejected without reason")
            )
            self._waiting_events[cid].set() # Unblock

    def request_approval(self, patch_result: PatchResult, session_id: str, correlation_id: str, timeout_seconds: int = 600) -> ApprovalResult:
        """
        Memblokir thread saat ini hingga Subscriber (CLI/Telegram) melempar
        ApprovalGranted atau ApprovalRejected.
        Timeout default adalah 10 menit (600 detik).
        """
        wait_event = threading.Event()
        self._waiting_events[correlation_id] = wait_event
        
        start_time = time.time()
        
        # Berteriak meminta persetujuan
        self.bus.publish(EventContext(
            event_name="BeforeApproval",
            timestamp=datetime.datetime.now().isoformat(),
            source="ApprovalEngine",
            priority=EventPriority.HIGH,
            session_id=session_id,
            correlation_id=correlation_id,
            payload={
                "patch_summary": patch_result.summary,
                "risk_level": patch_result.analysis.risk_level.value if patch_result.analysis else "UNKNOWN",
                "risk_score": patch_result.analysis.risk_score if patch_result.analysis else 0
            }
        ))
        
        # Membeku (Blok) sampai sinyal set() dipanggil atau timeout habis
        signaled = wait_event.wait(timeout=timeout_seconds)
        
        duration = time.time() - start_time
        
        # Membersihkan state
        del self._waiting_events[correlation_id]
        
        if not signaled:
            # Timeout
            result = ApprovalResult(
                is_approved=False,
                status=Status.FAILED,
                approver_id="System-Timeout",
                reason=f"Approval request timed out after {timeout_seconds} seconds",
                timeout_occurred=True
            )
        else:
            # Mengambil hasil yang sudah diset oleh handler
            result = self._approval_results.pop(correlation_id)
            
        # Memancarkan event konfirmasi
        self.bus.publish(EventContext(
            event_name="AfterApproval",
            timestamp=datetime.datetime.now().isoformat(),
            source="ApprovalEngine",
            priority=EventPriority.NORMAL,
            session_id=session_id,
            correlation_id=correlation_id,
            duration=duration,
            payload={
                "is_approved": result.is_approved,
                "approver_id": result.approver_id,
                "reason": result.reason
            }
        ))
        
        return result
