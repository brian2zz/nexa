from typing import Any, List, Protocol, runtime_checkable

@runtime_checkable
class StorageBackend(Protocol):
    """
    Abstraksi untuk penyimpanan observabilitas (Metrics & Audit).
    Bisa diimplementasikan sebagai JSONL, SQLite, Postgres, Memory, dll.
    """
    def write(self, collection: str, data: dict) -> None:
        """Menulis satu entri log ke collection (tabel/file)."""
        ...
        
    def read(self, collection: str, query: dict) -> List[dict]:
        """Membaca isi collection (untuk keperluan dashboard)."""
        ...
        
    def query(self, statement: str) -> Any:
        """Custom query raw (seperti SQL) jika dibutuhkan backend lanjutan."""
        ...
        
    def rotate(self) -> None:
        """Rotasi penyimpanan (misal menghapus log lama)."""
        ...
        
    def cleanup(self) -> None:
        """Membebaskan resource storage."""
        ...
