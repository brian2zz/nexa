import os
import shutil
import tempfile
import unittest
from typing import List

from nexa.core.events.bus import PipelineBus
from nexa.core.models.enums import Status
from nexa.core.models.dto.execution import ExecutionResult
from nexa.core.verification.engine import VerificationEngine
from nexa.core.execution.engine import ExecutionEngine

class TestVerificationEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.bus = PipelineBus(max_workers=4)
        self.verif_engine = VerificationEngine(repo_root=self.temp_dir, bus=self.bus)
        
        # Eksekusi engine disiapkan agar bisa menerima VerificationFailed
        self.exec_engine = ExecutionEngine(repo_root=self.temp_dir, bus=self.bus)
        
        self.valid_file = os.path.join(self.temp_dir, "valid.py")
        self.invalid_file = os.path.join(self.temp_dir, "invalid.py")
        
        with open(self.valid_file, 'w') as f:
            f.write("def hello():\n    return 'world'\n")
            
        with open(self.invalid_file, 'w') as f:
            f.write("def hello()\n    return 'world'\n") # Missing colon (Syntax Error)

    def tearDown(self):
        self.bus.shutdown(wait=True)
        shutil.rmtree(self.temp_dir)

    def test_verify_success(self):
        exec_res = ExecutionResult(success=True, status=Status.SUCCESS, files_modified=1, summary="")
        result = self.verif_engine.verify(exec_res, "sess-1", "corr-1", ["valid.py"])
        
        self.assertTrue(result.success)
        self.assertTrue(result.syntax_passed)
        self.assertEqual(len(result.error_messages), 0)

    def test_verify_syntax_error(self):
        exec_res = ExecutionResult(success=True, status=Status.SUCCESS, files_modified=1, summary="")
        result = self.verif_engine.verify(exec_res, "sess-2", "corr-2", ["invalid.py"])
        
        self.assertFalse(result.success)
        self.assertFalse(result.syntax_passed)
        self.assertTrue(len(result.error_messages) > 0)
        self.assertIn("Syntax Error", result.error_messages[0])

    def test_delayed_rollback_triggered(self):
        """
        Test bahwa jika verifikasi gagal, Event VerificationFailed memicu Rollback di ExecutionEngine.
        """
        # 1. Setup Session di BackupManager (Simulasi eksekusi yang sukses sebelum verifikasi)
        self.exec_engine.backup_manager.create_session("sess-3")
        self.exec_engine.backup_manager.backup(["invalid.py"]) # Backup file aslinya
        
        # 2. Modifikasi file untuk dirollback
        with open(self.invalid_file, 'w') as f:
            f.write("MODIFIED BY EXECUTION")
            
        # 3. Verifikasi gagal (Invalid file tetap invalid sintaksnya, atau kita cukup andalkan error mock)
        exec_res = ExecutionResult(success=True, status=Status.SUCCESS, files_modified=1, summary="")
        
        import time
        
        # Panggil verify. Ini akan memancarkan VerificationFailed.
        result = self.verif_engine.verify(exec_res, "sess-3", "corr-3", ["invalid.py"])
        self.assertFalse(result.success)
        
        # Tunggu sejenak agar background thread PipelineBus sempat memproses Event dan memanggil rollback
        time.sleep(1)
        
        # 4. Verifikasi Rollback
        with open(self.invalid_file, 'r') as f:
            content = f.read()
            # Harus kembali ke versi asli (Syntax Error), bukan "MODIFIED BY EXECUTION"
            self.assertEqual(content, "def hello()\n    return 'world'\n")

if __name__ == '__main__':
    unittest.main()
