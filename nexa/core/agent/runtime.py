import sys
import os
import logging

from nexa.core.events.bus import PipelineBus
from nexa.core.utils.path import get_project_nexa_dir
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
        self.tui_mode = False
        self.bus = PipelineBus(max_workers=2)
        
        # Inisialisasi Logger
        log_dir = os.path.join(get_project_nexa_dir(self.cwd), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "nexa-error.log")
        
        self.logger = logging.getLogger("NexaRuntime")
        self.logger.setLevel(logging.ERROR)
        if not self.logger.handlers:
            fh = logging.FileHandler(log_file)
            fh.setLevel(logging.ERROR)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
        
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
        from nexa.core.agent.tools.todo import register_todo_tools
        from nexa.core.agent.tools.execution_tools import register_execution_tools
        from nexa.core.agent.tools.web import register_web_tools
        from nexa.core.ai.mcp.manager import MCPManager
        
        self.tools = ToolRegistry()
        register_knowledge_tools(self.tools, self.cwd)
        register_pipeline_tools(self.tools, bus=self.bus, session_id_fn=lambda: self.session_id)
        self.todo_store = register_todo_tools(self.tools, self.cwd, self.bus, self.session_id)
        register_execution_tools(self.tools, self.cwd, bus=self.bus, session_id=self.session_id)
        register_web_tools(self.tools)
        
        # Inisialisasi MCP Tools
        self.mcp_manager = MCPManager(self.cwd)
        self.mcp_manager.load_and_register(self.tools)
        
        # Inisialisasi TUI Workflow (Sprint 4)
        from nexa.core.agent.workflow.interactive import ApprovalUI
        self.approval_ui = ApprovalUI(self.bus)
        self.bus.subscribe("BeforeApproval", self.approval_ui.handle_before_approval)
        
        def handle_execution_plan_submitted(context):
            """
            Dipicu ketika LLM memanggil submit_execution_plan.
            Meneruskan ExecutionPlan ke BeforeApproval untuk konfirmasi user.
            """
            import datetime
            from nexa.core.models.enums import EventPriority
            from nexa.core.events.bus import EventContext

            plan = context.payload.get("plan", {})
            files = context.payload.get("files", [])
            self.bus.publish(EventContext(
                event_name="BeforeApproval",
                timestamp=datetime.datetime.now().isoformat(),
                source="ExecutionPlanSubmitted",
                priority=EventPriority.HIGH,
                session_id=context.session_id,
                payload={"plan": plan, "files": files}
            ))

        self.bus.subscribe("ExecutionPlanSubmitted", handle_execution_plan_submitted)
        
        def handle_approval_granted(context):
            if context.payload.get("tool_approval", False):
                return
                
            import dataclasses
            plan = context.payload.get("plan", {})
            if dataclasses.is_dataclass(plan):
                # Check if it's PlanningResult, convert to ExecutionPlan
                if plan.__class__.__name__ == "PlanningResult":
                    from nexa.core.ai.planner.builder import PipelineBuilder
                    builder = PipelineBuilder()
                    exec_plan = builder.build(plan)
                    plan = dataclasses.asdict(exec_plan)
                else:
                    plan = dataclasses.asdict(plan)
            elif isinstance(plan, dict) and ("work_items" in plan or "summary" in plan) and "stages" not in plan:
                from nexa.core.ai.planner.schema import PlanningResult, WorkItem, ConfidenceAssessment
                from nexa.core.ai.planner.builder import PipelineBuilder
                work_items_raw = plan.get("work_items", [])
                work_items = [
                    WorkItem(
                        title=w.get("title", f"Step {i+1}"),
                        description=w.get("description", ""),
                        affected_files=w.get("affected_files", []),
                        objective=w.get("objective", "")
                    ) if isinstance(w, dict) else w
                    for i, w in enumerate(work_items_raw)
                ]
                planning_res = PlanningResult(
                    goal=plan.get("goal", "Execute Architecture Plan"),
                    summary=plan.get("summary", ""),
                    objective=plan.get("objective", ""),
                    constraints=plan.get("constraints", []),
                    work_items=work_items,
                    acceptance_criteria=[],
                    risk_analysis=[],
                    clarifications=[],
                    confidence=ConfidenceAssessment(level="HIGH", score=100, reason="Converted from dict plan", missing_information="")
                )
                builder = PipelineBuilder()
                exec_plan = builder.build(planning_res)
                plan = dataclasses.asdict(exec_plan)
                
            if not plan:
                print("[!] Execution dibatalkan: Tidak ada plan yang diterima.")
                return
            from nexa.core.pipeline.transaction import ExecutionTransaction
            transaction = ExecutionTransaction(self.cwd, plan)
            success, error_msg = transaction.execute()
            
            import datetime
            from nexa.core.models.enums import EventPriority
            from nexa.core.events.bus import EventContext

            if success:
                print("\n[✓] [Transaction Completed] Seluruh perubahan kode dan file berhasil diterapkan ke proyek!")
                self.bus.publish(EventContext(
                    event_name="AfterExecution",
                    timestamp=datetime.datetime.now().isoformat(),
                    source="ExecutionTransaction",
                    priority=EventPriority.NORMAL,
                    session_id=self.session_id,
                    payload={"success": True, "plan": plan, "walkthrough": error_msg}
                ))
            else:
                self.bus.publish(EventContext(
                    event_name="ExecutionFailed",
                    timestamp=datetime.datetime.now().isoformat(),
                    source="ExecutionTransaction",
                    priority=EventPriority.HIGH,
                    session_id=self.session_id,
                    payload={"error": error_msg, "plan": plan}
                ))
                print(f"\n[!] Memicu Auto-Recovery Nexa karena kegagalan eksekusi...")
                recovery_prompt = (
                    f"The previous Execution Plan failed during transaction with the following error:\n{error_msg}\n\n"
                    f"Please analyze why it failed and generate a revised Execution Plan to fix the issue."
                )
                
                from nexa.core.ai.agent_loop import AILoopEngine
                from nexa.core.ai.planner.schema import PlannerContext
                from nexa.core.utils.spinner import Spinner
                
                # Fetch limited context for recovery
                planner_context = PlannerContext(
                    project_path=self.cwd,
                    knowledge_context="",
                    project_facts={},
                    pinned_memory=[],
                    conversation_memory=self.memory.load_session_messages(self.session_id, limit=4),
                    user_goal=recovery_prompt
                )
                
                engine = AILoopEngine(bus=self.bus)
                with Spinner("Self-Healing: Regenerating & Repairing Plan..."):
                    report = engine.run_loop(planner_context, session_id=self.session_id, max_iterations=8)
                    
                if report.success:
                    GREEN = '\033[92m'
                    RESET = '\033[0m'
                    print(f"\n{GREEN}{report.to_markdown()}{RESET}\n")
                    
                    self.bus.publish(EventContext(
                        event_name="BeforeApproval",
                        timestamp=datetime.datetime.now().isoformat(),
                        source="AutoRecovery",
                        priority=EventPriority.HIGH,
                        session_id=self.session_id,
                        payload={
                            "files": getattr(report.plan, "affected_files", []) if not isinstance(report.plan, dict) else report.plan.get("affected_files", []),
                            "plan": report.plan
                        }
                    ))
                else:
                    print(f"\n[!] Auto-Recovery Failed: {report.error_message}\n")
            
        self.bus.subscribe("ApprovalGranted", handle_approval_granted)
        
        def handle_plan_revision(context):
            """
            Dipicu ketika user menekan [C] di Approval UI dan memberikan komentar/feedback.
            Nexa akan membuat ulang plan berdasarkan feedback tersebut.
            """
            from nexa.core.ai.planner import AIPlannerEngine, PlannerContext
            from nexa.core.utils.spinner import Spinner
            import datetime
            import dataclasses
            from nexa.core.models.enums import EventPriority
            from nexa.core.events.bus import EventContext
            
            comment = context.payload.get("comment", "")
            original_plan = context.payload.get("original_plan", {})
            
            if not comment:
                print("[!] Revision diminta tanpa komentar.")
                return
            
            # Serialize original plan to text for context
            if dataclasses.is_dataclass(original_plan):
                original_plan_text = str(dataclasses.asdict(original_plan))[:1000]
            elif isinstance(original_plan, dict):
                original_plan_text = str(original_plan)[:1000]
            else:
                original_plan_text = str(original_plan)[:1000]
            
            revision_goal = (
                f"PLAN REVISION REQUEST\n"
                f"User Feedback: {comment}\n\n"
                f"Original Plan Summary (for context):\n{original_plan_text}\n\n"
                f"Please generate a REVISED plan that incorporates the user's feedback above."
            )
            
            print(f"\n[*] Generating revised plan berdasarkan feedback Anda...\n")
            
            planner_context = PlannerContext(
                project_path=self.cwd,
                knowledge_context="",
                project_facts={},
                pinned_memory=[],
                conversation_memory=self.memory.load_session_messages(self.session_id, limit=4),
                user_goal=revision_goal
            )
            
            from nexa.core.ai.agent_loop import AILoopEngine
            engine = AILoopEngine(bus=self.bus)
            with Spinner("Revising Plan..."):
                report = engine.run_loop(planner_context, session_id=self.session_id, max_iterations=10)
                
            if report.success:
                GREEN = '\033[92m'
                RESET = '\033[0m'
                print(f"\n{GREEN}{report.to_markdown()}{RESET}\n")
                
                self.bus.publish(EventContext(
                    event_name="BeforeApproval",
                    timestamp=datetime.datetime.now().isoformat(),
                    source="PlanRevision",
                    priority=EventPriority.HIGH,
                    session_id=self.session_id,
                    payload={
                        "files": getattr(report.plan, "affected_files", []) if not isinstance(report.plan, dict) else report.plan.get("affected_files", []),
                        "plan": report.plan
                    }
                ))
            else:
                print(f"\n[!] Plan Revision Failed: {report.error_message}\n")
                
        self.bus.subscribe("PlanRevisionRequested", handle_plan_revision)
        
        # Inisialisasi Workspace Manager (Sprint 5)
        from nexa.core.agent.workspace import WorkspaceManager
        self.workspace = WorkspaceManager(self.cwd)
        
    def enable_tui_mode(self):
        """Enable TUI mode and disable legacy terminal approval UI."""
        self.tui_mode = True
        self.bus.unsubscribe("BeforeApproval", self.approval_ui.handle_before_approval)
        
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
            
        # Load persistent plan cache from SQLite or local workspace .nexa/plan.json
        self.last_plan = self.memory.load_session_plan(self.session_id)
        if not self.last_plan:
            local_plan_file = os.path.join(self.cwd, ".nexa", "plan.json")
            if os.path.exists(local_plan_file):
                try:
                    import json
                    with open(local_plan_file, "r", encoding="utf-8") as pf:
                        self.last_plan = json.load(pf)
                except Exception:
                    pass
            
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
                self.logger.exception("Agent Runtime Error occurred")
                print(f"\n[ERROR] Agent Runtime Error: {e}. Detail lengkap ada di .nexa/logs/nexa-error.log")
                
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
