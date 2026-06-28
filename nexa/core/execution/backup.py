import os
import json
import shutil
import hashlib
from typing import List, Dict, Optional
from datetime import datetime

class BackupManager:
    """
    Manager pencadangan deterministik. Mengelola lifecycle transaksi backup.
    Menggunakan penyimpanan disk (.nexa/backups) untuk ketahanan terhadap crash.
    """
    def __init__(self, repo_root: str, backup_dir_name: str = ".nexa/backups"):
        self.repo_root = repo_root
        self.backup_root = os.path.join(repo_root, backup_dir_name)
        self.current_session_id: Optional[str] = None
        self.session_dir: Optional[str] = None
        self.manifest: Dict = {}
        
        if not os.path.exists(self.backup_root):
            os.makedirs(self.backup_root, exist_ok=True)

    def _hash_file(self, filepath: str) -> Optional[str]:
        if not os.path.exists(filepath):
            return None
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def create_session(self, session_id: str) -> None:
        """Memulai sesi transaksi backup baru."""
        self.current_session_id = session_id
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = os.path.join(self.backup_root, f"{session_id}_{timestamp}")
        
        os.makedirs(self.session_dir, exist_ok=True)
        
        self.manifest = {
            "session_id": session_id,
            "timestamp": timestamp,
            "files": []
        }
        self._save_manifest()

    def _save_manifest(self) -> None:
        if not self.session_dir:
            return
        manifest_path = os.path.join(self.session_dir, "manifest.json")
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, indent=4)

    def backup(self, relative_paths: List[str]) -> bool:
        """Mencadangkan daftar file ke direktori session."""
        if not self.session_dir:
            raise RuntimeError("Session not created. Call create_session() first.")

        try:
            for rel_path in relative_paths:
                source_path = os.path.join(self.repo_root, rel_path)
                backup_filename = hashlib.md5(rel_path.encode('utf-8')).hexdigest() + ".bak"
                backup_path = os.path.join(self.session_dir, backup_filename)
                
                file_exists = os.path.exists(source_path)
                original_hash = self._hash_file(source_path) if file_exists else None
                
                if file_exists:
                    shutil.copy2(source_path, backup_path)
                    
                self.manifest["files"].append({
                    "relative_path": rel_path,
                    "backup_filename": backup_filename,
                    "original_hash": original_hash,
                    "existed": file_exists
                })
                
            self._save_manifest()
            return True
        except Exception as e:
            # Gagal saat melakukan backup, hentikan proses.
            return False

    def restore(self) -> bool:
        """Rollback: Mengembalikan file dari backup ke repo."""
        if not self.session_dir or not self.manifest.get("files"):
            return False
            
        try:
            for file_meta in self.manifest["files"]:
                rel_path = file_meta["relative_path"]
                target_path = os.path.join(self.repo_root, rel_path)
                
                if file_meta["existed"]:
                    # Kembalikan file
                    backup_path = os.path.join(self.session_dir, file_meta["backup_filename"])
                    shutil.copy2(backup_path, target_path)
                else:
                    # File sebelumnya tidak ada, berarti ini file baru. Hapus!
                    if os.path.exists(target_path):
                        os.remove(target_path)
            return True
        except Exception:
            return False

    def commit(self) -> None:
        """
        Transaksi selesai dan sukses.
        Bisa dipanggil untuk menandai manifest sebagai committed.
        """
        if self.session_dir:
            self.manifest["status"] = "COMMITTED"
            self._save_manifest()

    def cleanup(self) -> None:
        """
        (Opsional) Membersihkan session saat ini jika tidak diperlukan lagi.
        Atau biarkan untuk keperluan retention policy.
        """
        pass
