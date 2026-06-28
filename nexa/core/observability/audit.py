from nexa.core.storage.base import StorageBackend
from nexa.core.events.bus import PipelineBus
from nexa.core.models.events import EventContext

class AuditService:
    """
    Sistem pencatatan Black Box Nexa. Merekam semua pergerakan state
    dan manipulasi file yang bersifat destruktif atau mutating.
    """
    def __init__(self, storage: StorageBackend):
        self.storage = storage
        self.collection_name = "audit"

    def record_audit(self, context: EventContext) -> None:
        """Menangkap seluruh event kritis yang dikirim ke Audit."""
        data = {
            "correlation_id": context.correlation_id,
            "session_id": context.session_id,
            "timestamp": context.timestamp,
            "event_name": context.event_name,
            "source_engine": context.source,
            "payload": context.payload, # Harus json serializable (disarankan dikonversi dict)
        }
        self.storage.write(self.collection_name, data)

    def attach(self, bus: PipelineBus) -> None:
        """Mengikat Audit Service ke dalam PipelineBus secara otomatis."""
        
        # Patching Phase
        bus.subscribe("BeforePatch", self.record_audit)
        bus.subscribe("AfterPatch", self.record_audit)
        bus.subscribe("PatchFailed", self.record_audit)
        
        # Execution Phase
        bus.subscribe("BeforeExecution", self.record_audit)
        bus.subscribe("AfterExecution", self.record_audit)
        bus.subscribe("ExecutionFailed", self.record_audit)
        
        # Rollback Phase
        bus.subscribe("RollbackStarted", self.record_audit)
        bus.subscribe("RollbackCompleted", self.record_audit)
