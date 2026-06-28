import os
import hashlib
import time
import datetime
from typing import Optional
from nexa.core.events.bus import PipelineBus
from nexa.core.models.events import EventContext
from nexa.core.models.enums import EventPriority, Status
from nexa.core.models.dto.patch import PatchResult
from nexa.core.models.dto.execution import ExecutionResult
from nexa.core.execution.backup import BackupManager

class ExecutionEngine:
    """
    Engine deterministik yang menerapkan PatchResult ke filesystem secara nyata.
    Menggunakan mekanisme transaksi All-or-Nothing (Atomic).
    """
    def __init__(self, repo_root: str, bus: Optional[PipelineBus] = None):
        self.repo_root = repo_root
        self.bus = bus
        self.backup_manager = BackupManager(repo_root=repo_root)
        
        # Subscribe ke VerificationFailed untuk Delayed Rollback
        if self.bus:
            self.bus.subscribe("VerificationFailed", self._on_verification_failed)

    def _on_verification_failed(self, context: EventContext) -> None:
        # Jika Verification gagal, eksekusi rollback!
        session_id = context.session_id
        correlation_id = context.correlation_id
        
        # Agar mudah, kita akan menyimpan referensi session terakhir.
        if self.backup_manager.current_session_id == session_id:
            reason = "Verifikasi Gagal: " + str(context.payload.get("error_messages", []))
            self._do_rollback(session_id, correlation_id, time.time(), reason)

    def _hash_content(self, content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _read_file(self, filepath: str) -> Optional[str]:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def execute(self, patch_result: PatchResult, session_id: str, correlation_id: str) -> ExecutionResult:
        start_time = time.time()
        
        # 0. Sebelum eksekusi
        if self.bus:
            self.bus.publish(EventContext(
                event_name="BeforeExecution",
                timestamp=datetime.datetime.now().isoformat(),
                source="ExecutionEngine",
                priority=EventPriority.NORMAL,
                session_id=session_id,
                correlation_id=correlation_id,
                payload={"files_count": len(patch_result.patches)}
            ))

        if not patch_result.success or not patch_result.patches:
            return ExecutionResult(success=False, status=Status.FAILED, files_modified=0, summary="No valid patches to execute.")

        # Ekstrak daftar path yang akan dimodifikasi
        relative_paths = [patch.path for patch in patch_result.patches]
        
        # 1. Mulai Transaksi & Backup
        self.backup_manager.create_session(session_id)
        backup_success = self.backup_manager.backup(relative_paths)
        
        if not backup_success:
            return self._fail_and_emit(session_id, correlation_id, start_time, "Gagal membuat backup. Eksekusi dibatalkan demi keamanan.")

        failed_files = []
        
        # 2. Write Phase
        for patch in patch_result.patches:
            target_path = os.path.join(self.repo_root, patch.path)
            
            # Buat direktori jika belum ada
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            try:
                with open(target_path, 'w', encoding='utf-8') as f:
                    # Tulis seluruh konten baru
                    f.write(patch.new_content)
            except Exception as e:
                failed_files.append(patch.path)
                break # Segera keluar loop jika ada 1 saja gagal
                
        # Jika ada kegagalan Write -> Langsung Rollback
        if failed_files:
            return self._do_rollback(session_id, correlation_id, start_time, f"Write failed pada file: {failed_files[0]}")

        # 3. Verify Hash Phase (Deterministic Verification)
        for patch in patch_result.patches:
            target_path = os.path.join(self.repo_root, patch.path)
            actual_content = self._read_file(target_path)
            
            if actual_content is None:
                failed_files.append(patch.path)
                break
                
            actual_hash = self._hash_content(actual_content)
            # Patch engine idealnya mengisi new_hash berdasarkan konten utuh file, bukan hanya blok
            if patch.new_hash and patch.new_hash != actual_hash:
                failed_files.append(patch.path)
                break
                
        # Jika ada kegagalan Verify -> Rollback
        if failed_files:
            return self._do_rollback(session_id, correlation_id, start_time, f"Verify Hash gagal pada file: {failed_files[0]}. Kemungkinan race condition.")

        # 4. Commit Phase (Berhasil Penuh!)
        self.backup_manager.commit()
        
        duration = time.time() - start_time
        if self.bus:
            self.bus.publish(EventContext(
                event_name="AfterExecution",
                timestamp=datetime.datetime.now().isoformat(),
                source="ExecutionEngine",
                priority=EventPriority.NORMAL,
                session_id=session_id,
                correlation_id=correlation_id,
                duration=duration,
                payload={"files_modified": len(patch_result.patches)}
            ))
            
        return ExecutionResult(
            success=True,
            status=Status.SUCCESS,
            files_modified=len(patch_result.patches),
            summary=f"Berhasil mengaplikasikan {len(patch_result.patches)} file secara atomic."
        )

    def _fail_and_emit(self, session_id: str, correlation_id: str, start_time: float, reason: str) -> ExecutionResult:
        if self.bus:
            self.bus.publish(EventContext(
                event_name="ExecutionFailed",
                timestamp=datetime.datetime.now().isoformat(),
                source="ExecutionEngine",
                priority=EventPriority.HIGH,
                session_id=session_id,
                correlation_id=correlation_id,
                duration=time.time() - start_time,
                payload={"error": reason}
            ))
        return ExecutionResult(success=False, status=Status.FAILED, files_modified=0, summary=reason)
        
    def _do_rollback(self, session_id: str, correlation_id: str, start_time: float, reason: str) -> ExecutionResult:
        if self.bus:
            self.bus.publish(EventContext(
                event_name="RollbackStarted",
                timestamp=datetime.datetime.now().isoformat(),
                source="ExecutionEngine",
                priority=EventPriority.HIGH,
                session_id=session_id,
                correlation_id=correlation_id,
                payload={"reason": reason}
            ))
            
        restore_success = self.backup_manager.restore()
        
        if self.bus:
            self.bus.publish(EventContext(
                event_name="RollbackCompleted",
                timestamp=datetime.datetime.now().isoformat(),
                source="ExecutionEngine",
                priority=EventPriority.HIGH,
                session_id=session_id,
                correlation_id=correlation_id,
                payload={"restore_success": restore_success}
            ))
            
        # Return Execution Failed (karena ini asalnya dari gagal write/verify)
        return ExecutionResult(
            success=False, 
            status=Status.FAILED, 
            files_modified=0, 
            summary=f"Transaksi dibatalkan (All-or-Nothing). Rollback dijalankan. Alasan kegagalan: {reason}",
            rollback_occurred=True
        )
