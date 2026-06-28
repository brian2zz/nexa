from typing import Protocol, runtime_checkable
from nexa.core.models.events import EventContext

class PropagateHalted(Exception):
    """
    Eksepsi yang dilemparkan oleh Middleware jika ingin menghentikan PipelineBus
    secara paksa (Short-Circuit), misalnya karena pelanggaran keamanan.
    """
    pass

@runtime_checkable
class Middleware(Protocol):
    """
    Protokol untuk mencegat EventContext sebelum dan sesudah diproses oleh Subscriber.
    """
    def before_publish(self, context: EventContext) -> None:
        """Dipanggil sebelum event didistribusikan ke subscriber."""
        ...

    def after_publish(self, context: EventContext) -> None:
        """Dipanggil setelah seluruh subscriber selesai memproses event."""
        ...

    def on_error(self, context: EventContext, error: Exception) -> None:
        """Dipanggil jika terjadi kegagalan (crash) pada salah satu subscriber."""
        ...
