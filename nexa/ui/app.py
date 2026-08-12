import contextlib
import threading
import sys
from textual.app import App, ComposeResult
from textual.command import Provider, Hit
from functools import partial
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import Input, Static, Header, RichLog
from textual import work
from nexa.ui.bridge import Bridge, BusMessage
from textual.reactive import reactive
from nexa.ui.widgets.status_panel import StatusPanel
from nexa import __version__ as NEXA_VERSION
from nexa.config import Config
from nexa.ui.screens.approval import ApprovalModal
from nexa.ui.screens.palette import CommandPaletteModal, GenericSelectionModal, InputModal
from nexa.ui.widgets.chat_message import ChatMessage

class RedirectedStdout:
    """
    Scoped stdout shim: forwards complete lines from print() inside a worker
    command to the chat transcript. Used via contextlib.redirect_stdout so the
    global sys.stdout is never hijacked (C-3 / H-1).
    """
    def __init__(self, app):
        self._app = app
        self._buffer = ""
        self._lock = threading.Lock()

    def write(self, s):
        if "\r" in s:
            s = s.replace("\r", "")
            
        # Route spinner directly to the current AI message's thought block
        for c in "|/-\\":
            if f"[ {c} ]" in s:
                msg = s.split(f"[ {c} ]", 1)[-1].strip()
                try:
                    self._app.call_from_thread(self._app.add_thought_to_current, msg if msg else "Processing...")
                except RuntimeError:
                    pass
                return
                
        # Catch basic old spinner format just in case
        if any(f"[{c}]" in s for c in "|/-\\"):
            return
            
        if not s:
            return
            
        with self._lock:
            self._buffer += s
            if "\n" in self._buffer:
                lines = self._buffer.split("\n")
                self._buffer = lines[-1]
                for line in lines[:-1]:
                    if line:
                        self._emit(line + "\n")

    def _emit(self, line):
        try:
            self._app.call_from_thread(self._app.print_to_chat, line)
        except RuntimeError:
            self._app.print_to_chat(line)

    def flush(self):
        pass

class StatusBar(Static):
    status_text = reactive("Ready")
    
    def render(self):
        return self.status_text

class NexaCommandProvider(Provider):
    """Provides commands for the Nexa Command Palette."""
    
    _nexa_commands = [
        ("/help", "Show available commands"),
        ("/status", "Show runtime status"),
        ("/plan", "Generate an Execution Plan for a task"),
        ("/commands", "Show CLI commands for this project"),
        ("/history", "Show chat session history"),
        ("/session list", "Show all chat sessions"),
        ("/load", "Load a past chat session"),
        ("/clear", "Clear current chat session"),
        ("/select-provider", "Switch AI Provider"),
        ("/set-model", "Set active model for provider"),
        ("/set-api-key", "Set API Key for provider"),
        ("/facts", "Show project facts"),
        ("/pins", "Show pinned memory"),
        ("/pin", "Pin last AI response"),
        ("/clearpins", "Clear all pinned memory"),
        ("/exit", "Quit the application"),
    ]

    async def discover(self):
        for cmd, desc in self._nexa_commands:
            yield Hit(
                1.0,
                matcher.highlight(cmd + " - " + desc) if 'matcher' in locals() else cmd + " - " + desc,
                partial(self.app.handle_palette_result, cmd),
                help=desc
            )

    async def search(self, query: str):
        matcher = self.matcher(query)
        for cmd, desc in self._nexa_commands:
            score = matcher.match(cmd + " " + desc)
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(cmd + " - " + desc),
                    partial(self.app.handle_palette_result, cmd),
                    help=desc
                )

class NexaApp(App):
    COMMANDS = App.COMMANDS | {NexaCommandProvider}
    CSS = """
    Screen {
        layout: vertical;
    }
    #transcript {
        width: 1fr;
        height: 1fr;
        padding: 1;
        border: solid $surface;
    }
    #status-panel {
        width: 40;
        height: 1fr;
        border-left: solid $primary;
        background: $surface;
    }
    Input {
        dock: bottom;
    }
    StatusBar {
        dock: bottom;
        height: 1;
        background: $accent;
        color: $text;
        content-align: center middle;
    }
    """
    
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+k", "palette", "Command Palette"),
        ("pageup", "scroll_transcript_up", "Scroll Up"),
        ("pagedown", "scroll_transcript_down", "Scroll Down"),
    ]
    
    def action_scroll_transcript_up(self):
        self.query_one("#transcript").scroll_up(animate=False)
        
    def action_scroll_transcript_down(self):
        self.query_one("#transcript").scroll_down(animate=False)

    def __init__(self, command_handler, runtime):
        super().__init__()
        self.command_handler = command_handler
        self.runtime = runtime
        self.status_panel = StatusPanel(id="status-panel")
        
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with VerticalScroll(id="transcript"):
                # Initial greeting messages
                pass
            yield self.status_panel
            
        self.status_bar = StatusBar()
        yield self.status_bar
        yield Input(placeholder="Nexa> _", id="prompt-input")
        
    def on_mount(self):
        self.query_one("#prompt-input").focus()
        # Bridge the bus
        Bridge.subscribe(self.runtime.bus, "*", self)
        
        provider = Config.get("provider", "mock")
        model = Config.get(f"{provider}.model", "unknown")
        self.status_panel.set_info(
            version=NEXA_VERSION,
            project_path=self.runtime.cwd,
            provider=provider,
            model=model,
            session_id=self.runtime.session_id,
        )
        self.status_panel.set_provider_rates(provider)

        # Override Textual's dummy stdout with our RedirectedStdout
        self.original_stdout = sys.stdout
        sys.stdout = RedirectedStdout(self)
        
        self.current_ai_msg = None
        
        self.print_to_chat("Welcome to Nexa AI Interactive Shell (TUI).\nType /help for available commands or /exit to quit.", role="ai")
        
        self.set_interval(1.0, self.refresh_status_panel)

    def refresh_status_panel(self):
        provider = Config.get("provider", "mock")
        model = Config.get(f"{provider}.model", "unknown")
        self.status_panel.set_info(
            version=NEXA_VERSION,
            project_path=self.runtime.cwd,
            provider=provider,
            model=model,
            session_id=self.runtime.session_id,
        )

    def on_unmount(self):
        sys.stdout = getattr(self, "original_stdout", sys.stdout)

    def add_thought_to_current(self, thought: str):
        if not self.current_ai_msg:
            self.current_ai_msg = ChatMessage(role="ai")
            self.query_one("#transcript").mount(self.current_ai_msg)
            self.query_one("#transcript").scroll_end(animate=False)
            
        self.current_ai_msg.add_thought(thought)
        self.set_status(thought)
        
    def print_to_chat(self, text: str, role: str = "ai"):
        if role == "user":
            msg = ChatMessage(role="user", text=text)
            self.query_one("#transcript").mount(msg)
            self.query_one("#transcript").scroll_end(animate=False)
            self.current_ai_msg = None  # Reset current AI message so a new one is created next
        else:
            if not self.current_ai_msg:
                self.current_ai_msg = ChatMessage(role="ai")
                self.query_one("#transcript").mount(self.current_ai_msg)
                
            self.current_ai_msg.append_text(text)
            self.query_one("#transcript").scroll_end(animate=False)
        
    def on_input_submitted(self, event: Input.Submitted):
        cmd = event.value.strip()
        if not cmd:
            return
            
        event.input.value = ""
        
        # Open command palette directly if user just types "/"
        if cmd == "/":
            self.action_palette()
            return
            
        needs_args_or_modal = ["/select-provider", "/set-model", "/set-api-key", "/load", "/plan", "/facts set", "/facts remove", "/unpin", "/session enter", "/session delete"]
        
        # If user types exactly the command without args, trigger the palette handler (which shows modal or prepopulates input)
        if cmd in needs_args_or_modal:
            self.handle_palette_result(cmd)
            return
            
        # Do not echo slash commands to the chat transcript, to keep it clean like Opencode
        if not cmd.startswith("/"):
            self.print_to_chat(cmd, role="user")
            
        self.status_bar.status_text = "Processing..."
        self.run_command(cmd)
        
    @work(exclusive=True, thread=True)
    def run_command(self, cmd: str):
        with contextlib.redirect_stdout(RedirectedStdout(self)):
            try:
                should_continue = self.command_handler(cmd)
                if not should_continue:
                    self.app.call_from_thread(self.exit)
            except Exception as e:
                try:
                    self.app.call_from_thread(self.print_to_chat, f"Error: {e}")
                except RuntimeError:
                    self.print_to_chat(f"Error: {e}")
            finally:
                try:
                    self.app.call_from_thread(self.set_status, "Ready")
                except RuntimeError:
                    self.set_status("Ready")
            
    def set_status(self, text: str):
        self.status_bar.status_text = text
        
    _EVENT_LABELS = {
        "BeforePlanning": ("Planning started", "running"),
        "AfterPlanning":  ("Planning complete", "ok"),
        "PlanningFailed": ("Planning failed", "err"),
        "BeforePatch":    ("Patching started", "running"),
        "AfterPatch":     ("Patch applied", "ok"),
        "PatchFailed":    ("Patch failed", "err"),
        "BeforeExecution":("Execution started", "running"),
        "AfterExecution": ("Execution complete", "ok"),
        "ExecutionFailed":("Execution failed", "err"),
        "BeforeVerification":("Verification started", "running"),
        "AfterVerification": ("Verification complete", "ok"),
        "BeforeTransformation":("Transformation started", "running"),
        "AfterTransformation": ("Transformation complete", "ok"),
        "RetryStarted":   ("Retrying...", "running"),
        "RollbackStarted":("Rollback started", "running"),
        "RollbackCompleted":("Rollback complete", "ok"),
        "RecoverySucceeded":("Recovery complete", "ok"),
        "RecoveryFailed": ("Recovery failed", "err"),
    }

    def _human_event(self, ctx) -> str:
        label, _ = self._EVENT_LABELS.get(ctx.event_name, (ctx.event_name, "info"))
        return label

    def _status_of(self, ctx) -> str:
        _, status = self._EVENT_LABELS.get(ctx.event_name, ("", "info"))
        return status

    def on_bus_message(self, message: BusMessage):
        ctx = message.event_context
        payload = ctx.payload or {}
        
        if ctx.event_name == "TokenUsage":
            p = payload.get("prompt_tokens", 0) or 0
            c = payload.get("completion_tokens", 0) or 0
            self.status_panel.update_tokens(p, c)
            return

        if ctx.event_name in ("BeforePlanning", "PlanningFailed",
                              "BeforePatch", "AfterPatch", "PatchFailed",
                              "BeforeExecution", "AfterExecution", "ExecutionFailed",
                              "BeforeVerification", "AfterVerification",
                              "BeforeTransformation", "AfterTransformation",
                              "RetryStarted", "RollbackStarted", "RollbackCompleted",
                              "RecoverySucceeded", "RecoveryFailed"):
            self.status_panel.add_process(self._human_event(ctx), self._status_of(ctx))
            return

        if ctx.event_name == "AgentLoopIteration":
            iter_num = payload.get("iteration", 0)
            max_iter = payload.get("max_iterations", 15)
            self.call_from_thread(self.status_panel.add_process, f"Agent Loop [{iter_num}/{max_iter}]", "running")
            return
            
        if ctx.event_name == "UI_Print":
            msg = ctx.payload.get("message", "")
            role = ctx.payload.get("role", "ai")
            self.call_from_thread(self.print_to_chat, msg, role)
            return

        if ctx.event_name == "AgentTasksUpdated":
            tasks = payload.get("tasks", [])
            self.call_from_thread(self.status_panel.set_agent_tasks, tasks)
            return

            
        if ctx.event_name in ("AfterPlanning", "BeforeApproval"):
            if ctx.event_name == "AfterPlanning":
                self.status_panel.add_process("Planning complete", "ok")
            plan = payload.get("plan")
            work_items = (getattr(plan, "work_items", [])
                          if not isinstance(plan, dict)
                          else plan.get("work_items", []))
            if work_items:
                self.call_from_thread(self.status_panel.set_todos, work_items)

        if ctx.event_name == "ClarificationRequested":
            questions = payload.get("questions", [])
            from nexa.ui.screens.clarification import ClarificationModal
            
            def handle_clarification_result(answers):
                from nexa.core.events.bus import EventContext
                from nexa.core.models.enums import EventPriority
                import datetime
                self.runtime.bus.publish_async(EventContext(
                    event_name="ClarificationAnswered",
                    timestamp=datetime.datetime.now().isoformat(),
                    source="TUI",
                    priority=EventPriority.HIGH,
                    session_id=ctx.session_id,
                    payload={"answers": answers or {}}
                ))
                
            self.push_screen(ClarificationModal(questions), handle_clarification_result)
            return

        if ctx.event_name == "BeforeApproval":
            # Push ApprovalModal
            def handle_modal_result(result):
                if result:
                    action = result.get("action")
                    if action == "yes":
                        from nexa.core.events.bus import EventContext
                        from nexa.core.models.enums import EventPriority
                        import datetime
                        self.runtime.bus.publish_async(EventContext(
                            event_name="ApprovalGranted",
                            timestamp=datetime.datetime.now().isoformat(),
                            source="TUI",
                            priority=EventPriority.HIGH,
                            session_id=ctx.session_id,
                            payload={"plan": payload.get("plan")}
                        ))
                        self.print_to_chat("\n[Nexa] Execution Approved. Starting transaction...\n")
                    elif action == "no":
                        from nexa.core.events.bus import EventContext
                        from nexa.core.models.enums import EventPriority
                        import datetime
                        self.runtime.bus.publish_async(EventContext(
                            event_name="ApprovalRejected",
                            timestamp=datetime.datetime.now().isoformat(),
                            source="TUI",
                            priority=EventPriority.HIGH,
                            session_id=ctx.session_id,
                            payload={"plan": payload.get("plan")}
                        ))
                        self.print_to_chat("\n[Nexa] Execution Aborted by user.\n")
                    elif action == "comment":
                        comment = result.get("comment", "")
                        from nexa.core.events.bus import EventContext
                        from nexa.core.models.enums import EventPriority
                        import datetime
                        self.runtime.bus.publish_async(EventContext(
                            event_name="PlanRevisionRequested",
                            timestamp=datetime.datetime.now().isoformat(),
                            source="TUI",
                            priority=EventPriority.HIGH,
                            session_id=ctx.session_id,
                            payload={"comment": comment, "original_plan": payload.get("plan")}
                        ))
                        self.print_to_chat(f"\n[Nexa] Revision Requested: {comment}\n")
                        
            self.push_screen(ApprovalModal(ctx), handle_modal_result)
            
    def handle_palette_result(self, cmd: str) -> None:
        if cmd:
            if cmd == "/select-provider":
                opts = [
                    ("ollama", "Ollama (Local)"),
                    ("deepseek", "DeepSeek (Cloud)"),
                    ("groq", "Groq (Cloud)"),
                    ("gemini", "Gemini (Cloud)"),
                    ("mock", "Mock (Testing)")
                ]
                def _handle_provider(prov):
                    if prov:
                        if prov in ["deepseek", "groq", "gemini"]:
                            api_key = Config.get(f"{prov}.api_key", "")
                            if not api_key:
                                def _handle_key(key):
                                    if key:
                                        Config.set(f"{prov}.api_key", key)
                                    self.status_bar.status_text = "Processing..."
                                    self.run_command(f"{cmd} {prov}")
                                self.push_screen(InputModal(f"Enter API Key for {prov}:", password=True), _handle_key)
                                return
                        
                        self.status_bar.status_text = "Processing..."
                        self.run_command(f"{cmd} {prov}")
                self.push_screen(GenericSelectionModal("Select AI Provider", opts), _handle_provider)
                return

            if cmd == "/set-model":
                provider = Config.get("provider", "mock")
                if provider == "ollama":
                    opts = [("llama3.1", "llama3.1"), ("gemma:2b", "gemma:2b"), ("qwen3:14b", "qwen3:14b"), ("deepseek-coder", "deepseek-coder"), ("phi3", "phi3"), ("mistral", "mistral")]
                elif provider == "deepseek":
                    opts = [("deepseek-chat", "deepseek-chat"), ("deepseek-coder", "deepseek-coder")]
                elif provider == "groq":
                    opts = [("llama3-70b-8192", "llama3-70b-8192"), ("mixtral-8x7b-32768", "mixtral-8x7b-32768")]
                elif provider == "gemini":
                    opts = [("gemini-1.5-pro-latest", "gemini-1.5-pro"), ("gemini-1.5-flash-latest", "gemini-1.5-flash")]
                else:
                    opts = [("default", "default")]

                def _handle_model(mod):
                    if mod:
                        self.status_bar.status_text = "Processing..."
                        self.run_command(f"{cmd} {mod}")
                self.push_screen(GenericSelectionModal(f"Select Model for {provider}", opts), _handle_model)
                return

            needs_args = ["/set-api-key", "/load", "/plan", "/facts set", "/facts remove", "/unpin", "/session enter", "/session delete"]
            if cmd in needs_args:
                inp = self.query_one("#prompt-input")
                inp.value = cmd + " "
                inp.focus()
            else:
                self.status_bar.status_text = "Processing..."
                self.run_command(cmd)

    def action_palette(self) -> None:
        """Show Command Palette with Ctrl+K"""
        self.push_screen(CommandPaletteModal(), self.handle_palette_result)
