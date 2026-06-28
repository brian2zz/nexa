import uuid
from dataclasses import dataclass, field
from typing import Any, Protocol, Dict
from nexa.core.models.enums import EventPriority

@dataclass
class EventContext:
    event_name: str
    timestamp: str
    source: str
    priority: EventPriority
    session_id: str
    duration: float = 0.0
    payload: Any = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)

class EventPublisher(Protocol):
    """
    Protocol / Interface untuk EventManager.
    Implementasi aktual akan dikerjakan pada Phase Event.
    Semua engine harus menggunakan interface ini untuk melepas event.
    """
    def publish(self, event: EventContext) -> None:
        ...

    def publish_async(self, event: EventContext) -> None:
        ...
