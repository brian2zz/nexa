import json
import time
import datetime
import threading
from typing import Dict, Any, Optional

from nexa.core.ai.providers.factory import ProviderFactory
from nexa.core.events.bus import PipelineBus, EventContext
from nexa.core.models.enums import EventPriority
from nexa.core.agent.tools.registry import ToolRegistry
from nexa.core.ai.planner.schema import PlannerContext, PlanningResult, ConfidenceAssessment
from nexa.core.ai.planner.report import PlannerReport
from nexa.core.ai.planner.validator import PlanValidator

class AILoopEngine:
    """
    Phase 1: Iterative Autonomous Agent Loop
    Replaces the rigid linear AIPlannerEngine.
    """
    def __init__(self, bus: Optional[PipelineBus] = None):
        self.bus = bus
        self.provider = ProviderFactory.create()
        self.validator = PlanValidator()

    def _build_system_prompt(self, context: PlannerContext) -> str:
        prompt = (
            "You are Nexa AI, an autonomous software engineering agent in an active interactive session.\n"
            "You have full conversational memory of what you and the user discussed earlier in this session.\n"
            "When the user refers to previous context (e.g. 'terapkan planning tadi', 'lanjutkan', 'sesuai rencana kita'), you MUST build directly upon the blueprint and architecture agreed upon in earlier messages.\n"
            "You operate in an iterative loop. You can call tools to explore or write files, and provide your final response.\n"
        )
        prompt += f"\nProject Path: {context.project_path}\n"
        
        # Read AGENTS.md if it exists
        import os
        agents_md_path = os.path.join(context.project_path, "AGENTS.md")
        if os.path.exists(agents_md_path):
            try:
                with open(agents_md_path, 'r', encoding='utf-8') as f:
                    agents_content = f.read()
                prompt += f"\nProject Instructions (AGENTS.md):\n{agents_content}\n"
            except Exception as e:
                prompt += f"\nProject Instructions (AGENTS.md): Found but could not read ({e})\n"
        
        # Autonomous Skills Auto-Injection
        try:
            from nexa.core.ai.skills import SkillManager
            skill_mgr = SkillManager(context.project_path)
            skills_prompt = skill_mgr.format_skills_for_prompt()
            if skills_prompt:
                prompt += f"\n{skills_prompt}\n"
        except Exception:
            pass
        
        if context.project_facts:
            prompt += "\nProject Facts:\n"
            for k, v in context.project_facts.items():
                prompt += f"- {k}: {v}\n"
                
        if context.pinned_memory:
            prompt += "\nPinned Rules:\n"
            for p in context.pinned_memory:
                prompt += f"- {p['content']}\n"
                
        if context.knowledge_context:
            prompt += f"\nAdditional Context:\n{context.knowledge_context}\n"

        prompt += (
            "\n==================== NEXA FRAMEWORK & CLI COMMAND DIRECTORY ====================\n"
            "You are the Core Architect and Engine of Nexa Framework (which includes Nexa PHP, Nexa Flutter, Nexa Django, and Nexa AI).\n"
            "CRITICAL KNOWLEDGE ABOUT NEXA COMMANDS:\n"
            "1. Nexa PHP Commands (`nexa php <subcommand>`):\n"
            "   - `nexa php new <folder> [--frontend=vue|react]` : Initializes a new Nexa PHP project with skeleton structure.\n"
            "   - `nexa php generate [nexa.yaml]` : Scaffolds MVC models, controllers, routes, views, and migrations from schema.\n"
            "   - `nexa php make:module <name> [--enterprise]` : Creates a new domain module in `apps/<name>/`.\n"
            "   - `nexa php make:model <Name> <App>` : Creates a Doctrine ORM entity model in `apps/<App>/Models/`.\n"
            "   - `nexa php make:controller <Name> <App>` : Creates a REST API CRUD controller in `apps/<App>/Controllers/`.\n"
            "   - `php bin/nexa makemigrations && php bin/nexa migrate` : Creates and executes database migrations.\n"
            "   - `nexa php run` : Runs the local HTTP development server at http://127.0.0.1:8000.\n"
            "\n"
            "2. Nexa Flutter Commands (`nexa flutter <subcommand>`):\n"
            "   - `nexa flutter new <name>` : Creates a new Flutter enterprise project.\n"
            "   - `nexa flutter create-module <name>` : Scaffolds a clean architecture Flutter feature module.\n"
            "   - `nexa flutter gen-model` : Generates Freezed / JSON-serializable Dart models.\n"
            "   - `nexa flutter run` : Runs the Flutter application.\n"
            "\n"
            "3. Nexa Django Commands (`nexa django <subcommand>`):\n"
            "   - `nexa django new <name>` : Creates a new modular Django project.\n"
            "   - `nexa django startapp <name>` : Scaffolds a Django app domain.\n"
            "   - `nexa django make:api` : Generates Django REST Framework viewsets and serializers.\n"
            "   - `nexa django run` : Runs Django dev server.\n"
            "\n"
            "4. Nexa AI Shell Interactive Slash Commands:\n"
            "   - `/help` : Displays the full command and shortcut directory.\n"
            "   - `/commands` : Lists all registered CLI subcommands across all groups.\n"
            "   - `/plan <goal>` : Generates an architectural plan.\n"
            "   - `/mode` : Toggles between PLAN (read-only analysis) and BUILD (code editing).\n"
            "   - `/model` / `/models` : Selects active AI model.\n"
            "   - `/key` / `/set-api-key` : Sets provider API key.\n"
            "   - `/select-provider` : Switches active AI provider (deepseek, gemini, groq, ollama).\n"
            "   - `/sessions` / `/load` : Manages and loads chat sessions.\n"
            "   - `/undo` / `/redo` : Reverts or reapplies changes with rollback.\n"
            "   - `/editor` : Opens external editor (Notepad / VS Code) for long input.\n"
            "\n"
            "5. Keyboard Shortcuts:\n"
            "   - `Ctrl + K` : Opens Command Palette.\n"
            "   - `Tab` : Toggles PLAN / BUILD mode.\n"
            "   - `Ctrl + V` / Right-Click : Pastes clipboard content.\n"
            "   - `Ctrl + Y` : Copies latest AI response.\n"
            "   - `ESC` : Dismisses/cancels any active modal popup.\n"
            "\nDATA ANALYSIS & QUERY PROTOCOL (SCRATCH SCRIPT & AUTO-CLEANUP LIKE ANTIGRAVITY/OPENCODE):\n"
            "When asked to analyze data, search deep codebase patterns, test functions, or query database state:\n"
            "1. CREATE SCRATCH SCRIPT: Use `write_file` to create a lightweight temporary script (e.g. `query_temp.py` or `.nexa/scratch/query.py`).\n"
            "2. EXECUTE QUERY: Use `run_bash_command` to execute the script and retrieve the raw records/output.\n"
            "3. AUTO-CLEANUP: Immediately call `delete_file` to remove the temporary scratch script so the workspace remains 100% clean.\n"
            "4. SYNTHESIZE & PRESENT: Synthesize the extracted results into a clear, professional Markdown report with tables and actionable insights for the user.\n"
            "=================================================================================\n\n"
            "\nNEXA FRAMEWORK EXPERT ARCHITECT CONVENTIONS (ANTIGRAVITY BLUEPRINT FORMAT):\n"
            "You are the Lead Solutions Architect and Core Engineer of Nexa Framework.\n"
            "When the user asks to design, plan, or scaffold an application (e.g. laundry system, pos, inventory, blog, etc.):\n"
            "1. INVESTIGATE: Use your tools (file_tree, file_read, directory_list, search_files) to inspect what already exists.\n"
            "2. REPORT FINDINGS: In your blueprint, explain what folders/files already exist (e.g. if 'sistem_laundry' or 'nexa.yaml' already exists), explain their structure, and recommend how to use or extend them.\n"
            "3. ARCHITECTURE BLUEPRINT: In your final JSON output, the `summary` field MUST be a detailed, rich, professional Markdown Architectural Blueprint containing:\n"
            "   - **🔍 Temuan Struktur Proyek & Analisis Folder** (Analisis folder/file yang ada dan saran pengembangannya).\n"
            "   - **🏛️ Ringkasan Arsitektur & Entitas Bisnis** (Deskripsi alur bisnis & aktor yang terlibat).\n"
            "   - **📊 Tabel Database & Model Entitas** (Format tabel Markdown dengan kolom: Nama Entitas, Kolom / Field, Tipe Data, Relasi & Keterangan).\n"
            "   - **📄 Skema Lengkap `nexa.yaml`** (Blok kode YAML lengkap siap pakai dengan semua entitas, field tipe data, dan relasi foreign key).\n"
            "   - **🚀 Strategi Eksekusi & Endpoint Controller** (Daftar route/endpoint API yang akan digenerate).\n\n"
            "EXPECTED FINAL JSON OUTPUT FORMAT:\n"
            "{\n"
            "  \"summary\": \"## 🏛️ Cetak Biru Arsitektur: Sistem Laundry\\n\\n### 🔍 Temuan Struktur Proyek\\nDitemukan folder `sistem_laundry` di workspace... Disarankan untuk memanfaatkan struktur ini.\\n\\n### 📊 Skema Database & Entitas Model\\n| Entitas | Field / Kolom | Tipe Data | Relasi & Deskripsi |\\n|---|---|---|---|\\n| **Customer** | name, phone, address | string, string, text | Pelanggan laundry |\\n| **LaundryPackage** | name, price_per_kg, duration_hours | string, decimal, int | Jenis paket cuci |\\n| **Order** | customer_id, package_id, total_weight, total_price, status | fk:Customer, fk:LaundryPackage, decimal, decimal, enum | Transaksi pemesanan |\\n| **Payment** | order_id, amount, payment_method, payment_status | fk:Order, decimal, string, enum | Riwayat pembayaran |\\n\\n### 📄 Konfigurasi Skema `nexa.yaml`\\n```yaml\\nversion: \\\"1.0\\\"\\nproject:\\n  name: \\\"laundry_system\\\"\\n  type: \\\"php\\\"\\napps:\\n  - name: \\\"core\\\"\\n    models:\\n      - name: \\\"Customer\\\"\\n        fields:\\n          name: \\\"string:100\\\"\\n          phone: \\\"string:20\\\"\\n          address: \\\"text,nullable\\\"\\n      - name: \\\"LaundryPackage\\\"\\n        fields:\\n          name: \\\"string:100\\\"\\n          price_per_kg: \\\"decimal:10,2\\\"\\n          duration_hours: \\\"integer\\\"\\n      - name: \\\"Order\\\"\\n        fields:\\n          customer_id: \\\"foreign:Customer\\\"\\n          package_id: \\\"foreign:LaundryPackage\\\"\\n          total_weight: \\\"decimal:8,2\\\"\\n          total_price: \\\"decimal:10,2\\\"\\n          status: \\\"string:20\\\"\\n      - name: \\\"Payment\\\"\\n        fields:\\n          order_id: \\\"foreign:Order\\\"\\n          amount: \\\"decimal:10,2\\\"\\n          payment_status: \\\"string:20\\\"\\n```\",\n"
            "  \"objective\": \"Build Laundry System with Nexa PHP\",\n"
            "  \"work_items\": [\n"
            "    {\"title\": \"1. Generate nexa.yaml Schema\", \"description\": \"Create nexa.yaml containing Customer, LaundryPackage, Order, Payment models\", \"affected_files\": [\"nexa.yaml\"], \"objective\": \"Define architecture schema\"},\n"
            "    {\"title\": \"2. Run Nexa Scaffolding Engine\", \"description\": \"Execute 'nexa php generate nexa.yaml' to create MVC models, controllers, views, routes, and run database migrations\", \"affected_files\": [\"app/\", \"database/\", \"routes/\"], \"objective\": \"Generate code and database\"}\n"
            "  ],\n"
            "  \"acceptance_criteria\": [\n"
            "    {\"description\": \"Database tables created and migrated\", \"priority\": \"MUST\", \"verification_method\": \"DB Check\"}\n"
            "  ],\n"
            "  \"risk_analysis\": [\n"
            "    {\"category\": \"General\", \"probability\": \"LOW\", \"impact\": \"LOW\", \"mitigation\": \"Auto-rollback enabled\"}\n"
            "  ]\n"
            "}\n"
        )
        return prompt

    def run_loop(self, context: PlannerContext, session_id: int = 0, max_iterations: int = 15) -> PlannerReport:
        start_time = time.time()
        
        sys_prompt = self._build_system_prompt(context)
        messages = [{"role": "system", "content": sys_prompt}]
        
        # Inject conversation history so follow-up commands like "terapkan", "lanjutkan", "execute" understand past context
        if context.conversation_memory:
            for msg in context.conversation_memory[-6:]:
                m_role = "user" if msg.get("role") == "user" else "assistant"
                m_content = msg.get("content", "")
                if m_content:
                    messages.append({"role": m_role, "content": m_content})
                    
        messages.append({"role": "user", "content": context.user_goal})
        
        # Load tools based on active mode:
        # In PLAN mode: Read-only knowledge tools (explore/analyze) so LLM creates full architectural plan
        # In BUILD mode: Knowledge + Execution tools (write/edit/run)
        from nexa.config import Config
        agent_mode = Config.get("agent.mode", "PLAN").upper()
        
        from nexa.core.agent.tools.knowledge import register_knowledge_tools
        registry = ToolRegistry()
        register_knowledge_tools(registry, context.project_path)
        
        if agent_mode == "BUILD":
            from nexa.core.agent.tools.execution_tools import register_execution_tools
            register_execution_tools(registry, context.project_path, bus=self.bus, session_id=session_id)
            
        tool_schemas = registry.get_all_schemas()
        
        iteration = 0
        final_json_content = None
        
        while iteration < max_iterations:
            iteration += 1
            if self.bus:
                self.bus.publish(EventContext(
                    event_name="AgentLoopIteration",
                    timestamp=datetime.datetime.now().isoformat(),
                    source="AILoopEngine",
                    priority=EventPriority.NORMAL,
                    session_id=session_id,
                    payload={"iteration": iteration, "max_iterations": max_iterations}
                ))

            try:
                # If reaching 3 iterations, prompt final synthesis while keeping tools active
                if iteration == 3:
                    messages.append({
                        "role": "user",
                        "content": (
                            "Berdasarkan semua hasil investigasi file/folder di atas, tolong SEKARANG berikan Blueprint Arsitektur dan Rencana Eksekusi lengkap.\n"
                            "Sertakan temuan struktur file yang ada (misal folder sistem_laundry / nexa.yaml), strategi pengembangannya, "
                            "tabel database & model relasi, skema `nexa.yaml` lengkap, serta daftar langkah kerja (`work_items`) dalam format JSON final yang ditentukan."
                        )
                    })
                resp = self.provider.generate(messages, tools=tool_schemas)
            except Exception as e:
                return PlannerReport(success=False, error_message=f"LLM Provider Error: {str(e)}")
            
            content = resp.get("content", "")
            tool_calls = resp.get("tool_calls", [])
            
            # Helper to check if content contains a valid JSON plan
            def _has_plan_structure(text: str) -> bool:
                if not text:
                    return False
                t = text.strip()
                if "```json" in t:
                    t = t.split("```json")[1].split("```")[0].strip()
                elif "```" in t:
                    t = t.split("```")[1].strip()
                if not t.startswith("{"):
                    import re
                    m = re.search(r"(\{.*\})", t, re.DOTALL)
                    if m:
                        t = m.group(1).strip()
                try:
                    p = json.loads(t)
                    if isinstance(p, dict) and ("summary" in p or "work_items" in p or "objective" in p):
                        return True
                except Exception:
                    pass
                return False

            # If LLM returned content without tool calls:
            if content and not tool_calls:
                # If LLM returned structured JSON plan or comprehensive blueprint markdown:
                if _has_plan_structure(content) or ("##" in content and "```" in content):
                    final_json_content = content
                    break
                elif iteration < 3 and tool_schemas:
                    # LLM returned an intermediate conversational remark (e.g. "Mari saya periksa...")
                    # Append thought and guide LLM to deliver the full Architecture Blueprint & Plan JSON
                    assistant_msg = {"role": "assistant", "content": content}
                    messages.append(assistant_msg)
                    messages.append({
                        "role": "user",
                        "content": (
                            "Bagus. Berdasarkan investigasi tersebut, tolong langsung susun dan berikan Cetak Biru Arsitektur "
                            "(Architecture Blueprint) lengkap, tabel database/model, skema `nexa.yaml` lengkap, dan daftar langkah kerja (`work_items`) "
                            "sekarang dalam format JSON yang telah ditentukan."
                        )
                    })
                    continue
                else:
                    final_json_content = content
                    break
            
            assistant_msg = {"role": "assistant"}
            if content:
                assistant_msg["content"] = content
            if tool_calls:
                assistant_msg["tool_calls"] = tool_calls
                
            messages.append(assistant_msg)
            
            if tool_calls:
                # LLM requested tool execution
                for tcall in tool_calls:
                    tname = tcall.get("function", {}).get("name")
                    targs_str = tcall.get("function", {}).get("arguments", "{}")
                    
                    try:
                        targs = json.loads(targs_str) if isinstance(targs_str, str) else targs_str
                    except Exception:
                        targs = {}
                        
                    if self.bus:
                        self.bus.publish(EventContext(
                            event_name="ToolCalled",
                            timestamp=datetime.datetime.now().isoformat(),
                            source="AILoopEngine",
                            priority=EventPriority.NORMAL,
                            session_id=session_id,
                            payload={"tool_name": tname, "status": "running"}
                        ))
                    
                    needs_approval = tname in ["run_bash_command", "write_file", "edit_file_content"]
                    
                    if needs_approval and self.bus:
                        # Construct a dummy plan for ApprovalModal
                        from nexa.core.pipeline.execution.models import ExecutionPlan, ExecutionStage, CommandStep, ExecutionStrategy
                        
                        dummy_step = CommandStep(
                            id=f"tool_{iteration}",
                            executable=tname,
                            args=[json.dumps(targs)],
                            strategy=ExecutionStrategy.STOP_ON_ERROR,
                            raw_command=f"Tool Call: {tname}({json.dumps(targs, indent=2)})"
                        )
                        dummy_plan = ExecutionPlan(
                            stages=[ExecutionStage(name=f"Agent Tool Request: {tname}", steps=[dummy_step])],
                            can_rollback=False
                        )
                        
                        approval_event = threading.Event()
                        user_action = {"action": "no"}
                        
                        def on_approval_granted(ctx):
                            nonlocal user_action
                            if ctx.event_name == "ApprovalGranted":
                                user_action["action"] = "yes"
                                approval_event.set()
                        def on_planning_revision(ctx):
                            nonlocal user_action
                            if ctx.event_name == "PlanRevisionRequested":
                                user_action["action"] = "comment"
                                user_action["comment"] = ctx.payload.get("comment", "")
                                approval_event.set()
                        def on_approval_rejected(ctx):
                            nonlocal user_action
                            if ctx.event_name == "ApprovalRejected":
                                user_action["action"] = "no"
                                approval_event.set()
                        
                        self.bus.subscribe("ApprovalGranted", on_approval_granted)
                        self.bus.subscribe("PlanRevisionRequested", on_planning_revision)
                        self.bus.subscribe("ApprovalRejected", on_approval_rejected)
                        
                        try:
                            self.bus.publish_async(EventContext(
                                event_name="BeforeApproval",
                                timestamp=datetime.datetime.now().isoformat(),
                                source="AILoopEngine",
                                priority=EventPriority.HIGH,
                                session_id=session_id,
                                payload={"plan": dummy_plan, "tool_approval": True}
                            ))
                            
                            if self.bus:
                                self.bus.publish(EventContext(
                                    event_name="ToolCalled",
                                    timestamp=datetime.datetime.now().isoformat(),
                                    source="AILoopEngine",
                                    priority=EventPriority.NORMAL,
                                    session_id=session_id,
                                    payload={"tool_name": f"Awaiting approval for {tname}", "status": "running"}
                                ))
                            if not approval_event.wait(timeout=60.0):
                                user_action["action"] = "timeout"
                        finally:
                            self.bus.unsubscribe("ApprovalGranted", on_approval_granted)
                            self.bus.unsubscribe("PlanRevisionRequested", on_planning_revision)
                            self.bus.unsubscribe("ApprovalRejected", on_approval_rejected)
                        
                        if user_action["action"] == "yes":
                            if self.bus:
                                self.bus.publish(EventContext(
                                    event_name="ToolCalled",
                                    timestamp=datetime.datetime.now().isoformat(),
                                    source="AILoopEngine",
                                    priority=EventPriority.NORMAL,
                                    session_id=session_id,
                                    payload={"tool_name": tname, "status": "success"}
                                ))
                            result_str = str(registry.execute(tname, targs))
                        elif user_action["action"] == "comment":
                            if self.bus:
                                self.bus.publish(EventContext(
                                    event_name="ToolCalled",
                                    timestamp=datetime.datetime.now().isoformat(),
                                    source="AILoopEngine",
                                    priority=EventPriority.NORMAL,
                                    session_id=session_id,
                                    payload={"tool_name": tname, "status": "error"}
                                ))
                            result_str = f"Execution aborted. User commented: {user_action['comment']}"
                        else:
                            if self.bus:
                                self.bus.publish(EventContext(
                                    event_name="ToolCalled",
                                    timestamp=datetime.datetime.now().isoformat(),
                                    source="AILoopEngine",
                                    priority=EventPriority.NORMAL,
                                    session_id=session_id,
                                    payload={"tool_name": tname, "status": "error"}
                                ))
                            if user_action.get("action") == "timeout":
                                result_str = "Execution aborted due to timeout."
                            else:
                                result_str = "Execution aborted by user."
                    else:
                        # Auto-execute safe tools
                        if self.bus:
                            self.bus.publish(EventContext(
                                event_name="ToolCalled",
                                timestamp=datetime.datetime.now().isoformat(),
                                source="AILoopEngine",
                                priority=EventPriority.NORMAL,
                                session_id=session_id,
                                payload={"tool_name": tname, "status": "success"}
                            ))
                        result_str = str(registry.execute(tname, targs))
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tcall.get("id", ""),
                        "name": tname,
                        "content": result_str
                    })
            else:
                # No tool calls, assume LLM provided the final plan
                final_json_content = content
                break
                
        if not final_json_content:
            # Force one final synthesis generation with strict schema requirement
            try:
                synthesis_instruction = (
                    "Berdasarkan semua hasil investigasi file/folder di atas, tolong SEKARANG berikan Blueprint Arsitektur dan Rencana Eksekusi lengkap.\n"
                    "CRITICAL: Pada field `summary`, tuliskan temuan folder/file yang ada (misal folder sistem_laundry / nexa.yaml), strategi pengembangannya, "
                    "Cetak Biru Arsitektur, Tabel Database/Model relasi, dan skema `nexa.yaml` lengkap dalam bahasa Indonesia markdown!\n"
                    "Pada field `work_items`, sebutkan daftar langkah tugas implementasi."
                )
                final_resp = self.provider.generate(messages + [{
                    "role": "user",
                    "content": synthesis_instruction
                }], tools=tool_schemas)
                final_json_content = final_resp.get("content", "")
            except Exception:
                final_json_content = ""
            
        # Parse final plan JSON with ultra-resilient extraction
        try:
            import re
            cleaned_json = final_json_content.strip()
            if "```json" in cleaned_json:
                cleaned_json = cleaned_json.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_json:
                cleaned_json = cleaned_json.split("```")[1].strip()
                
            # If still not starting with {, search for the first JSON object
            if not cleaned_json.startswith("{"):
                match = re.search(r"(\{.*\})", cleaned_json, re.DOTALL)
                if match:
                    cleaned_json = match.group(1).strip()
                
            data = json.loads(cleaned_json)
        except Exception:
            # Fallback for plain text natural language response
            data = {
                "summary": final_json_content.strip(),
                "objective": context.user_goal,
                "work_items": [],
                "acceptance_criteria": [],
                "risk_analysis": [],
                "clarifications": []
            }
            
        from nexa.core.ai.planner.schema import WorkItem, AcceptanceCriterion, RiskItem
        
        work_items = []
        for wi in data.get("work_items", []):
            work_items.append(WorkItem(
                title=wi.get("title", ""),
                description=wi.get("description", ""),
                affected_files=wi.get("affected_files", []),
                objective=wi.get("objective", "")
            ))
            
        # Resilient fallback: ensure work_items is not empty if blueprint/summary exists
        if not work_items and final_json_content:
            summary_lower = final_json_content.lower()
            affected = []
            if "nexa.yaml" in summary_lower or "yaml" in summary_lower:
                affected.append("nexa.yaml")
            work_items.append(WorkItem(
                title="1. Generate Architecture & Configuration Schema",
                description="Create or update nexa.yaml with defined models and relationship fields",
                affected_files=affected if affected else ["nexa.yaml"],
                objective="Define schema models and configurations"
            ))
            work_items.append(WorkItem(
                title="2. Execute Scaffolding & Database Migration",
                description="Generate MVC boilerplate, controllers, models, routes, and execute migrations",
                affected_files=["app/", "database/", "routes/"],
                objective="Scaffold project structure and database tables"
            ))
            
        ac = []
        for a in data.get("acceptance_criteria", []):
            ac.append(AcceptanceCriterion(
                description=a.get("description", ""),
                priority=a.get("priority", "MUST"),
                verification_method=a.get("verification_method", "")
            ))
            
        ra = []
        for r in data.get("risk_analysis", []):
            ra.append(RiskItem(
                category=r.get("category", "General"),
                probability=r.get("probability", "MEDIUM"),
                impact=r.get("impact", "MEDIUM"),
                mitigation=r.get("mitigation", "")
            ))
            
        validated_plan = PlanningResult(
            goal=context.user_goal,
            summary=data.get("summary", "Agent Loop completed successfully."),
            objective=data.get("objective", ""),
            constraints=data.get("constraints", []),
            work_items=work_items,
            acceptance_criteria=ac,
            risk_analysis=ra,
            clarifications=data.get("clarifications", []),
            confidence=ConfidenceAssessment(level="HIGH", score=100, reason="Iterative tool usage", missing_information="")
        )
        
        if self.bus:
            self.bus.publish(EventContext(
                event_name="AfterPlanning",
                timestamp=datetime.datetime.now().isoformat(),
                source="AILoopEngine",
                priority=EventPriority.NORMAL,
                session_id=session_id,
                duration=time.time() - start_time,
                payload={"plan": validated_plan}
            ))
            
        return PlannerReport(success=True, error_message="", plan=validated_plan)
