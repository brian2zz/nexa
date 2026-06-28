import sys
import os
from typing import Optional
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

from nexa.config import Config
from nexa.core.events.bus import PipelineBus
from nexa.core.ai.memory.core import ChatMemoryManager
from nexa.core.agent.conversation import ConversationManager

class NexaAgentRuntime:
    """
    Otak utama Nexa untuk Phase 4.
    Menjaga agent tetap hidup (Looping), menangani interupsi (Ctrl+C),
    serta mengelola konteks percakapan.
    """
    def __init__(self, cwd: str):
        self.cwd = cwd
        self.is_running = False
        self.bus = PipelineBus(max_workers=2)
        
        # Inisialisasi sistem memori (Sprint 2)
        self.memory = ChatMemoryManager()
        self.conversation_manager = ConversationManager(self.memory)
        
        # Pemulihan Sesi (Sprint 6)
        from nexa.core.agent.session import SessionRecoveryManager
        self.session_recovery = SessionRecoveryManager(self.memory)
        
        # Sesi akan diinisialisasi saat start_loop() dipanggil
        self.session_id = None
        
        # Inisialisasi ToolRegistry (Sprint 3)
        from nexa.core.agent.tools.registry import ToolRegistry
        from nexa.core.agent.tools.knowledge import register_knowledge_tools
        from nexa.core.agent.tools.pipeline import register_pipeline_tools
        
        self.tools = ToolRegistry()
        register_knowledge_tools(self.tools, self.cwd)
        register_pipeline_tools(self.tools)
        
        # Inisialisasi TUI Workflow (Sprint 4)
        from nexa.core.agent.workflow.interactive import ApprovalUI
        self.approval_ui = ApprovalUI(self.bus)
        self.bus.subscribe("BeforeApproval", self.approval_ui.handle_before_approval)
        
        def handle_approval_granted(context):
            import dataclasses
            plan = context.payload.get("plan", {})
            if dataclasses.is_dataclass(plan):
                plan = dataclasses.asdict(plan)
                
            if not plan:
                print("[!] Execution dibatalkan: Tidak ada plan yang diterima.")
                return
            from nexa.core.pipeline.transaction import ExecutionTransaction
            transaction = ExecutionTransaction(self.cwd, plan)
            transaction.execute()
            
        self.bus.subscribe("ApprovalGranted", handle_approval_granted)
        # Inisialisasi Workspace Manager (Sprint 5)
        from nexa.core.agent.workspace import WorkspaceManager
        self.workspace = WorkspaceManager(self.cwd)
        
    def start_loop(self, get_input_fn, command_handler=None):
        """
        Memulai siklus hidup agent.
        """
        self.is_running = True
        
        # 0. Pemulihan Sesi (Sprint 6)
        recovered_id = self.session_recovery.prompt_recovery(self.cwd)
        if recovered_id is not None:
            self.session_id = recovered_id
        else:
            self.session_id = self.memory.create_session(self.cwd)
            
        print("\n[Nexa Agent Runtime Started]")
        
        # Cetak Intelijen Workspace ke Terminal (Simulasi)
        sys_prompt = self.workspace.generate_system_prompt()
        print("\n=== SYSTEM PROMPT ===")
        print(sys_prompt)
        print("=====================\n")
        
        print("Ketik '/exit' atau tekan Ctrl+C untuk keluar secara aman.\n")
        
        while self.is_running:
            try:
                # 1. Wait for Prompt
                user_input = get_input_fn()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['/exit', '/quit', 'exit', 'quit']:
                    self._graceful_shutdown()
                    break
                    
                # 2. Command Handler (Legacy & Built-in commands)
                if command_handler and command_handler(user_input):
                    continue
                    
                # 3. Process Response
                self._handle_input(user_input)
                
            except KeyboardInterrupt:
                # Menangkap Ctrl+C
                print("\n[!] Menerima sinyal interupsi (Ctrl+C).")
                self._graceful_shutdown()
                break
            except EOFError:
                # Menangkap Ctrl+D
                self._graceful_shutdown()
                break
            except Exception as e:
                print(f"\n[ERROR] Agent Runtime Error: {e}")
                
    def _handle_input(self, user_input: str):
        """
        Di Sprint 2, kita menguji ConversationManager dengan menyimpan 
        percakapan dan mencetak Context Bundle.
        """
        # 1. Simpan pesan user
        self.memory.save_message(self.session_id, "user", user_input)
        
        # 2. Tarik Context Bundle (yang sudah di-Summarize jika overflow)
        context_bundle = self.conversation_manager.get_context_bundle(self.session_id)
        
        # 3. Echo kembali sebagai "assistant" untuk Sprint 2
        mock_response = f"Echo (Konteks ditarik: {len(context_bundle)} pesan): {user_input}"
        self.memory.save_message(self.session_id, "assistant", mock_response)
        
        print(f"\n[Nexa] {mock_response}")
        print(f"       (Isi Context Bundle: {[m['role'] for m in context_bundle]})\n")
        
    def _graceful_shutdown(self):
        """
        Menghentikan seluruh proses, mematikan bus, menyimpan sesi, dll.
        """
        print("[*] Melakukan Graceful Shutdown...")
        self.is_running = False
        self.bus.shutdown(wait=True)
        print("[*] Nexa Agent berhasil dimatikan. Sampai jumpa!")
        sys.exit(0)
