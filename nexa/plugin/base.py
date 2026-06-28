from typing import List, Protocol, runtime_checkable
from nexa.core.events.bus import PipelineBus

@runtime_checkable
class NexaPlugin(Protocol):
    """
    SDK Base Interface untuk membangun ekstensi pihak ketiga (Misal: TelegramPlugin, VSCodePlugin).
    Plugin harus mematuhi siklus hidup ini.
    """
    
    def get_name(self) -> str:
        """Mengembalikan nama unik plugin."""
        ...
        
    def get_version(self) -> str:
        """Mengembalikan versi plugin."""
        ...
        
    def get_description(self) -> str:
        """Mengembalikan deskripsi singkat plugin."""
        ...
        
    def get_dependencies(self) -> List[str]:
        """Daftar modul yang dibutuhkan (jika ada)."""
        ...
        
    def initialize(self) -> None:
        """Dipanggil saat plugin diinisialisasi oleh sistem."""
        ...
        
    def on_register(self, bus: PipelineBus) -> None:
        """
        Dipanggil saat plugin didaftarkan ke PipelineBus.
        Di sinilah Plugin melakukan `bus.subscribe(...)`.
        """
        ...
        
    def health_check(self) -> bool:
        """Sistem pengecekan kesehatan plugin (jika return False, plugin akan di-unload)."""
        ...
        
    def shutdown(self) -> None:
        """Dipanggil saat aplikasi mati (Graceful Shutdown)."""
        ...
