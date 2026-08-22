from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Static, Input, Markdown
from textual.containers import Vertical, Horizontal, VerticalScroll
from nexa.core.events.bus import EventContext

class ApprovalModal(ModalScreen[dict]):
    """
    Modal screen for Plan Execution Approval.
    Returns a dict with 'action' ("yes", "no", "comment") and 'comment' (str).
    """
    
    CSS = """
    ApprovalModal {
        align: center middle;
        background: $background 80%;
    }
    
    #approval-dialog {
        padding: 1 2;
        width: 75%;
        height: 80%;
        border: thick $primary;
        background: $surface;
    }
    
    #approval-title {
        text-align: center;
        text-style: bold;
        padding-bottom: 1;
    }
    
    #approval-buttons {
        align: center middle;
        height: 3;
        margin-top: 1;
        dock: bottom;
    }
    
    #approval-comment {
        margin-top: 1;
        display: none;
        dock: bottom;
    }
    
    #approval-markdown-scroll {
        height: 1fr;
        border: solid $primary;
        margin: 1 0;
        scrollbar-size: 1 1;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    def __init__(self, context: EventContext, **kwargs):
        super().__init__(**kwargs)
        self.event_context = context
        self.plan = context.payload.get("plan", {})
        
    def _format_plan_markdown(self) -> str:
        """Formats any plan or tool approval into clean, human-readable Markdown."""
        import json
        payload = self.event_context.payload if self.event_context else {}
        plan = self.plan

        # 1. If it's a PlanningResult with rich markdown
        if hasattr(plan, "work_items") or hasattr(plan, "to_markdown"):
            from nexa.core.ai.planner.formatter import PlanFormatter
            try:
                return PlanFormatter().to_markdown(plan)
            except Exception:
                pass

        # 2. If it's an ExecutionPlan (Tool Request or Pipeline Stages)
        stages = getattr(plan, "stages", []) if not isinstance(plan, dict) else plan.get("stages", [])
        if stages:
            md = "### ⚠️ Konfirmasi Izin Tindakan / Eksekusi Perintah\n\n"
            md += "Nexa membutuhkan persetujuan Anda untuk menjalankan instruksi berikut:\n\n"
            
            for stage_idx, stage in enumerate(stages, 1):
                s_name = getattr(stage, "name", f"Tahap {stage_idx}") if not isinstance(stage, dict) else stage.get("name", f"Tahap {stage_idx}")
                steps = getattr(stage, "steps", []) if not isinstance(stage, dict) else stage.get("steps", [])
                
                md += f"#### 🔹 {s_name}\n\n"
                for step_idx, step in enumerate(steps, 1):
                    executable = getattr(step, "executable", "") if not isinstance(step, dict) else step.get("executable", "")
                    raw_cmd = getattr(step, "raw_command", "") if not isinstance(step, dict) else step.get("raw_command", "")
                    args = getattr(step, "args", []) if not isinstance(step, dict) else step.get("args", [])
                    risk = getattr(step, "risk_level", "NORMAL") if not isinstance(step, dict) else step.get("risk_level", "NORMAL")
                    
                    cmd_display = ""
                    file_target = ""
                    if args and isinstance(args, list) and len(args) > 0:
                        try:
                            first_arg = args[0]
                            if isinstance(first_arg, str) and (first_arg.startswith("{") or "command" in first_arg):
                                parsed_args = json.loads(first_arg)
                                cmd_display = parsed_args.get("command", "")
                                file_target = parsed_args.get("path", "") or parsed_args.get("filepath", "") or parsed_args.get("target", "")
                        except Exception:
                            pass
                    
                    if not cmd_display and raw_cmd:
                        cmd_display = raw_cmd
                    if not cmd_display and args:
                        cmd_display = " ".join(str(a) for a in args)
                        
                    md += f"**🛠️ Tool:** `{executable}` &nbsp;&nbsp;|&nbsp;&nbsp; **⚠️ Risiko:** **{risk}**\n"
                    if file_target:
                        md += f"- **Target File:** `{file_target}`\n"
                    if cmd_display:
                        md += f"\n**⚡ Perintah Terminal yang Akan Dijalankan:**\n```bash\n{cmd_display}\n```\n"
                    md += "\n"
            
            md += "\n> Tekan **Yes, Execute (Enter / Y)** untuk menjalankan atau **No, Abort (N / ESC)** untuk membatalkan.\n"
            return md

        # 3. If it's a dict containing summary or work_items
        if isinstance(plan, dict):
            if "summary" in plan or "work_items" in plan:
                summary = plan.get("summary", "")
                work_items = plan.get("work_items", [])
                md = "### 📋 Konfirmasi Rencana Perubahan (Plan Execution)\n\n"
                if summary:
                    md += f"{summary}\n\n"
                if work_items:
                    md += "### 🛠️ Daftar Langkah Kerja (Work Items):\n"
                    for i, w in enumerate(work_items, 1):
                        if isinstance(w, dict):
                            title = w.get("title", f"Langkah {i}")
                            desc = w.get("description", "")
                            files = w.get("affected_files", [])
                            md += f"**{i}. {title}**\n"
                            if desc:
                                md += f"  - *Deskripsi:* {desc}\n"
                            if files:
                                md += f"  - *File Terkait:* `{', '.join(files)}`\n"
                return md

        return f"```\n{str(plan)}\n```"

    def compose(self) -> ComposeResult:
        with Vertical(id="approval-dialog"):
            yield Static("⚠️ Approval Required for Execution Plan", id="approval-title")
            
            with VerticalScroll(id="approval-markdown-scroll"):
                try:
                    md_content = self._format_plan_markdown()
                except Exception as e:
                    md_content = f"Failed to render plan details: {e}"
                    
                yield Markdown(md_content)
            
            with Horizontal(id="approval-buttons"):
                yield Button("Yes, Execute", variant="success", id="btn-yes")
                yield Button("No, Abort", variant="error", id="btn-no")
                yield Button("Provide Feedback (C)", variant="primary", id="btn-comment")
                
            yield Input(placeholder="Type your feedback here and press Enter...", id="approval-comment")

    def on_mount(self):
        # Auto focus on Yes button so user can immediately press Enter / Space
        self.query_one("#btn-yes", Button).focus()

    def on_key(self, event) -> None:
        if event.key in ("y", "Y"):
            self.dismiss({"action": "yes", "comment": ""})
        elif event.key in ("n", "N", "escape"):
            self.dismiss({"action": "no", "comment": ""})
        elif event.key in ("c", "C"):
            comment_input = self.query_one("#approval-comment", Input)
            comment_input.display = True
            comment_input.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-yes":
            self.dismiss({"action": "yes", "comment": ""})
        elif event.button.id == "btn-no":
            self.dismiss({"action": "no", "comment": ""})
        elif event.button.id == "btn-comment":
            # Show input field
            comment_input = self.query_one("#approval-comment", Input)
            comment_input.display = True
            comment_input.focus()
            
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "approval-comment":
            comment = event.value.strip()
            if comment:
                self.dismiss({"action": "comment", "comment": comment})
