import unittest
import threading
import time
from nexa.core.events.bus import PipelineBus
from nexa.core.models.events import EventContext
from nexa.core.approval.engine import ApprovalEngine
from nexa.core.models.dto.patch import PatchResult
from nexa.core.ai.patching.risk_analyzer import PatchAnalysis
from nexa.core.models.enums import Status, RiskLevel

class MockTelegramSubscriber:
    """Mensimulasikan Bot Telegram yang meng-klik tombol 'Approve' setelah 0.5 detik."""
    def __init__(self, bus: PipelineBus, approve: bool = True):
        self.bus = bus
        self.approve = approve
        self.bus.subscribe("BeforeApproval", self.on_before_approval)
        
    def on_before_approval(self, context: EventContext):
        # Berjalan di thread threadpoolexecutor
        def delay_and_reply():
            time.sleep(0.5)
            event_name = "ApprovalGranted" if self.approve else "ApprovalRejected"
            self.bus.emit(EventContext(
                event_name=event_name,
                timestamp="now",
                source="MockTelegram",
                priority=context.priority,
                session_id=context.session_id,
                correlation_id=context.correlation_id,
                payload={"approver_id": "Telegram-Admin", "reason": "Looks good" if self.approve else "Too risky"}
            ))
            
        threading.Thread(target=delay_and_reply).start()

class TestApprovalEngine(unittest.TestCase):
    def setUp(self):
        self.bus = PipelineBus(max_workers=4)
        self.engine = ApprovalEngine(self.bus)
        
        # Dummy Patch Result
        self.patch_result = PatchResult(
            success=True,
            status=Status.SUCCESS,
            patches=[],
            summary="Test Patch",
            analysis=PatchAnalysis(risk_score=10, risk_level=RiskLevel.LOW, needs_human_approval=False)
        )

    def tearDown(self):
        self.bus.shutdown(wait=True)

    def test_approval_granted(self):
        subscriber = MockTelegramSubscriber(self.bus, approve=True)
        
        result = self.engine.request_approval(
            patch_result=self.patch_result,
            session_id="session-1",
            correlation_id="corr-1",
            timeout_seconds=5
        )
        
        self.assertTrue(result.is_approved)
        self.assertEqual(result.approver_id, "Telegram-Admin")
        self.assertFalse(result.timeout_occurred)

    def test_approval_rejected(self):
        subscriber = MockTelegramSubscriber(self.bus, approve=False)
        
        result = self.engine.request_approval(
            patch_result=self.patch_result,
            session_id="session-2",
            correlation_id="corr-2",
            timeout_seconds=5
        )
        
        self.assertFalse(result.is_approved)
        self.assertEqual(result.approver_id, "Telegram-Admin")
        self.assertEqual(result.reason, "Too risky")
        self.assertFalse(result.timeout_occurred)

    def test_approval_timeout(self):
        # Tidak ada subscriber yang menjawab
        result = self.engine.request_approval(
            patch_result=self.patch_result,
            session_id="session-3",
            correlation_id="corr-3",
            timeout_seconds=1 # Cepat saja timeoutnya
        )
        
        self.assertFalse(result.is_approved)
        self.assertTrue(result.timeout_occurred)
        self.assertEqual(result.approver_id, "System-Timeout")

if __name__ == '__main__':
    unittest.main()
