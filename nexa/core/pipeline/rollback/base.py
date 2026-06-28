from abc import ABC, abstractmethod
from typing import List

class RollbackStrategy(ABC):
    """
    Interface untuk semua strategi rollback di Nexa.
    """
    
    @abstractmethod
    def backup(self, files: List[str]) -> bool:
        """
        Melakukan backup sebelum file dimodifikasi.
        """
        pass
        
    @abstractmethod
    def rollback(self) -> bool:
        """
        Mengembalikan file ke kondisi backup jika terjadi kegagalan.
        """
        pass
        
    @abstractmethod
    def commit(self) -> bool:
        """
        Membersihkan backup jika transaksi berhasil.
        """
        pass
