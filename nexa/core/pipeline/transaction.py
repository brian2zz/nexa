import time
from enum import Enum
from typing import List, Any, Tuple
from nexa.core.pipeline.transformation import TransformationEngine, TransformationResult
from nexa.core.pipeline.patch import PatchEngine, PatchApplier, PatchResult
from nexa.core.pipeline.command import TerminalRunner
from nexa.core.pipeline.rollback.backup import BackupRollbackStrategy
from nexa.core.pipeline.verification import VerificationPipeline

class TransactionState(Enum):
    PENDING = 1
    BACKUP_CREATED = 2
    PATCH_APPLIED = 3
    COMMAND_EXECUTED = 4
    VERIFIED = 5
    COMMITTED = 6
    ROLLING_BACK = 7
    ROLLED_BACK = 8
    FAILED = 9

class ExecutionTransaction:
    """
    Orkestrator utama (State Machine) untuk mengeksekusi Approved Patch secara aman.
    """
    def __init__(self, cwd: str, plan: dict):
        self.cwd = cwd
        self.plan = plan
        self.state = TransactionState.PENDING
        
        self.transform_engine = TransformationEngine()
        self.patch_engine = PatchEngine()
        self.patch_applier = PatchApplier(cwd=cwd)
        self.terminal_runner = TerminalRunner(cwd=cwd)
        self.rollback_strategy = BackupRollbackStrategy(cwd=cwd)
        self.verification_pipeline = VerificationPipeline(cwd=cwd)
        
    def execute(self) -> Tuple[bool, str]:
        print("\n[Transaction] Memulai transaksi eksekusi...")
        
        try:
            # 1. Transform & Patch
            print("[Transaction] [1/5] Melakukan kalkulasi Patch...")
            transform_results = self.transform_engine.transform(self.plan)
            patches = self.patch_engine.calculate(transform_results)
            
            # Ekstrak daftar file yang akan dimodifikasi
            files_to_modify = [p.target for p in patches if p.action in ["CREATE", "MODIFY", "DELETE"]]
            
            # 2. Backup
            print(f"[Transaction] [2/5] Membackup {len(files_to_modify)} file...")
            if files_to_modify:
                if not self.rollback_strategy.backup(files_to_modify):
                    self.state = TransactionState.FAILED
                    return False, "Gagal membuat backup."
            self.state = TransactionState.BACKUP_CREATED
            
            # 3. Apply Patch
            print("[Transaction] [3/5] Menerapkan Patch ke filesystem...")
            for patch in patches:
                if patch.action in ["CREATE", "MODIFY", "DELETE"]:
                    if not self.patch_applier.apply(patch):
                        self._trigger_rollback("Gagal menerapkan patch")
                        return False, f"Gagal menerapkan patch pada file {patch.target}"
            self.state = TransactionState.PATCH_APPLIED
            
            # 4. Execute Commands
            print("[Transaction] [4/5] Mengeksekusi instruksi terminal...")
            for patch in patches:
                if patch.action == "COMMAND" and patch.command:
                    success, msg = self.terminal_runner.execute(patch.command)
                    if not success:
                        self._trigger_rollback(f"Command gagal: {msg}")
                        return False, f"Terminal command failed: {patch.command}\nError: {msg}"
            self.state = TransactionState.COMMAND_EXECUTED
            
            # 5. Verify
            print("[Transaction] [5/5] Memvalidasi perubahan...")
            success, msg = self.verification_pipeline.run_all()
            if not success:
                self._trigger_rollback(f"Verifikasi gagal: {msg}")
                return False, f"Verification failed: {msg}"
            self.state = TransactionState.VERIFIED
            
            # 6. Commit
            print("[Transaction] [SUCCESS] Transaksi berhasil! Membersihkan backup...")
            self.rollback_strategy.commit()
            self.state = TransactionState.COMMITTED
            return True, ""
            
        except Exception as e:
            self._trigger_rollback(f"Unexpected Error: {e}")
            return False, f"Unexpected Transaction Error: {e}"
            
    def _trigger_rollback(self, reason: str):
        print(f"\n[!] Transaksi Gagal ({reason}). Melakukan Rollback...")
        self.state = TransactionState.ROLLING_BACK
        
        if self.rollback_strategy.rollback():
            print("[*] Rollback berhasil. Sistem dikembalikan ke state awal.")
            self.state = TransactionState.ROLLED_BACK
        else:
            print("[!] FATAL: Rollback gagal. Sistem dalam state tidak stabil.")
            self.state = TransactionState.FAILED
