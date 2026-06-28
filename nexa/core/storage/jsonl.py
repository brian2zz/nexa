import os
import json
import threading
from typing import Any, List, Dict
from nexa.core.storage.base import StorageBackend

class JsonlStorageBackend(StorageBackend):
    def __init__(self, log_dir: str = ".nexa/logs"):
        self.log_dir = log_dir
        self._lock = threading.Lock()
        
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)
            
    def _get_path(self, collection: str) -> str:
        return os.path.join(self.log_dir, f"{collection}.jsonl")
        
    def write(self, collection: str, data: dict) -> None:
        file_path = self._get_path(collection)
        with self._lock:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(data) + "\n")
                
    def read(self, collection: str, query: dict) -> List[dict]:
        file_path = self._get_path(collection)
        if not os.path.exists(file_path):
            return []
            
        results = []
        with self._lock:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    item = json.loads(line)
                    # Filter sederhana
                    match = all(item.get(k) == v for k, v in query.items())
                    if match:
                        results.append(item)
        return results
        
    def query(self, statement: str) -> Any:
        # Belum didukung di JSONL (harus pakai parser raw atau SQLite nantinya)
        raise NotImplementedError("Raw queries not supported by JSONL.")
        
    def rotate(self) -> None:
        # Implementasi sederhana: tidak melakukan apapun di versi awal
        pass
        
    def cleanup(self) -> None:
        pass
