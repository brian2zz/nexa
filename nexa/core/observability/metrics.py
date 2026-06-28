from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from nexa.core.storage.base import StorageBackend
from nexa.core.events.bus import PipelineBus
from nexa.core.models.events import EventContext

@dataclass
class RuntimeMetrics:
    duration: float
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None

@dataclass
class BusinessMetrics:
    patch_count: int = 0
    approval_count: int = 0
    execution_success_rate: float = 0.0

class MetricsCollector:
    """
    Dedicated Subscriber untuk mengumpulkan metrik performa (Runtime)
    dan metrik fungsional (Business) di seluruh siklus Nexa.
    """
    def __init__(self, storage: StorageBackend):
        self.storage = storage
        self.collection_name = "metrics"

    def record_runtime(self, context: EventContext) -> None:
        """Dipanggil dari event loop (misal: event berakhiran 'Completed')"""
        payload = context.payload if isinstance(context.payload, dict) else {}
        
        metrics = RuntimeMetrics(
            duration=context.duration,
            memory_usage=payload.get("memory_usage"),
            cpu_usage=payload.get("cpu_usage"),
            prompt_tokens=payload.get("prompt_tokens"),
            completion_tokens=payload.get("completion_tokens")
        )
        
        data = {
            "type": "runtime",
            "correlation_id": context.correlation_id,
            "source": context.source,
            "metrics": asdict(metrics),
            "timestamp": context.timestamp
        }
        self.storage.write(self.collection_name, data)

    def record_business(self, context: EventContext) -> None:
        """Dipanggil saat event bisnis besar (Misal: PatchSuccess)."""
        data = {
            "type": "business",
            "correlation_id": context.correlation_id,
            "event": context.event_name,
            "timestamp": context.timestamp
        }
        self.storage.write(self.collection_name, data)

    def attach(self, bus: PipelineBus) -> None:
        """Utility untuk menempelkan diri secara otomatis ke Bus."""
        bus.subscribe("*Completed", self.record_runtime)
        bus.subscribe("AfterPatch", self.record_business)
        bus.subscribe("AfterExecution", self.record_business)
