import os
import shutil
import tempfile
import unittest
import hashlib
from typing import List

from nexa.core.events.bus import PipelineBus
from nexa.core.models.events import EventContext
from nexa.core.models.enums import Status, Operation
from nexa.core.models.dto.patch import PatchResult, PatchObject
from nexa.core.execution.engine import ExecutionEngine
from nexa.core.execution.backup import BackupManager

def _hash(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

class TestExecutionEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.bus = PipelineBus(max_workers=2)
        self.engine = ExecutionEngine(repo_root=self.temp_dir, bus=self.bus)
        
        # Setup file awal
        self.file1_path = os.path.join(self.temp_dir, "file1.txt")
        self.file2_path = os.path.join(self.temp_dir, "file2.txt")
        
        with open(self.file1_path, 'w', encoding='utf-8') as f:
            f.write("Line 1\nLine 2\n")
            
        with open(self.file2_path, 'w', encoding='utf-8') as f:
            f.write("A\nB\n")

    def tearDown(self):
        self.bus.shutdown(wait=True)
        shutil.rmtree(self.temp_dir)

    def test_successful_execution(self):
        # Skenario 100% Berhasil
        new_content1 = "Line 1 modified\nLine 2\n"
        new_content2 = "A\nB modified\n"
        
        patch1 = PatchObject(
            path="file1.txt",
            operation=Operation.MODIFY,
            old_hash=_hash("Line 1\nLine 2\n"),
            new_hash=_hash(new_content1),
            new_content=new_content1
        )
        patch2 = PatchObject(
            path="file2.txt",
            operation=Operation.MODIFY,
            old_hash=_hash("A\nB\n"),
            new_hash=_hash(new_content2),
            new_content=new_content2
        )
        
        pr = PatchResult(success=True, status=Status.SUCCESS, patches=[patch1, patch2], summary="Test", additions=0, deletions=0)
        
        result = self.engine.execute(pr, session_id="sess-1", correlation_id="corr-1")
        
        self.assertTrue(result.success)
        self.assertEqual(result.files_modified, 2)
        self.assertFalse(result.rollback_occurred)
        
        # Verify file content
        with open(self.file1_path, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), new_content1)
            
    def test_rollback_on_hash_mismatch(self):
        # Skenario salah satu hash meleset (misal file dimodifikasi pihak lain di tengah jalan, 
        # atau algoritma patch meleset memprediksi new_hash)
        
        new_content1 = "Content 1 OK"
        new_content2 = "Content 2 FAIL"
        
        patch1 = PatchObject(
            path="file1.txt",
            operation=Operation.MODIFY,
            old_hash=_hash("Line 1\nLine 2\n"),
            new_hash=_hash(new_content1), # Benar
            new_content=new_content1
        )
        patch2 = PatchObject(
            path="file2.txt",
            operation=Operation.MODIFY,
            old_hash=_hash("A\nB\n"),
            new_hash=_hash("WRONG_HASH_PREDICTION"), # Hash meleset
            new_content=new_content2
        )
        
        pr = PatchResult(success=True, status=Status.SUCCESS, patches=[patch1, patch2], summary="Test", additions=0, deletions=0)
        
        # Execution
        result = self.engine.execute(pr, session_id="sess-2", correlation_id="corr-2")
        
        self.assertFalse(result.success)
        self.assertTrue(result.rollback_occurred)
        self.assertEqual(result.files_modified, 0)
        
        # Verify bahwa file DIBALIKAN KE KONDISI SEMULA (All-or-Nothing)
        with open(self.file1_path, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), "Line 1\nLine 2\n") # Bukan "Content 1 OK"
            
        with open(self.file2_path, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), "A\nB\n")

if __name__ == '__main__':
    unittest.main()
