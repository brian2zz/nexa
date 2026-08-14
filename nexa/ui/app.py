import contextlib
import threading
import sys
from textual.app import App, ComposeResult
from textual.command import Provider, Hit
from functools import partial
from textual.containers import VerticalScroll, Horizontal, Vertical
from textual.widgets import Input, Static, Header, RichLog, OptionList, TextArea
from textual.widgets.option_list import Option
from textual import work, events
from nexa.ui.bridge import Bridge, BusMessage
from textual.reactive import reactive
from nexa.ui.widgets.status_panel import StatusPanel
from nexa import __version__ as NEXA_VERSION
from nexa.config import Config
from nexa.ui.screens.approval import ApprovalModal
from nexa.ui.screens.palette import CommandPaletteModal, GenericSelectionModal, InputModal, SessionSelectionModal
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
    mode = reactive("PLAN")  # "PLAN" (Read-only analysis / grill-me) or "BUILD" (Write & Edit code)
    
    def render(self):
        mode_badge = f"[bold green]⚒ BUILD[/bold green]" if self.mode == "BUILD" else f"[bold yellow]🔍 PLAN (Read-Only)[/bold yellow]"
        return f"{self.status_text} | Mode: {mode_badge} [dim](Press TAB to toggle)[/dim]"

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
        background: #0d1117;
        overflow: hidden;
    }
    Header {
        dock: top;
        background: #161b22;
        color: #58a6ff;
        text-style: bold;
    }
    #main-area {
        width: 1fr;
        height: 1fr;
    }
    #transcript {
        width: 1fr;
        height: 100%;
        padding: 1 2;
        background: #0d1117;
        scrollbar-size: 1 1;
        scrollbar-color: #30363d #161b22;
    }
    #status-panel {
        width: 42;
        height: 100%;
        border-left: solid #30363d;
        background: #161b22;
        padding: 1;
        scrollbar-size: 1 1;
    }
    #bottom-dock {
        dock: bottom;
        height: auto;
        width: 100%;
        background: #0d1117;
    }
    Input {
        width: 100%;
        background: #161b22;
        border: tall #30363d;
        color: #f0f6fc;
        padding: 0 1;
        margin: 0;
    }
    Input:focus {
        border: tall #58a6ff;
    }
    #suggestion-box {
        width: 100%;
        height: auto;
        max-height: 10;
        background: #161b22;
        border: round #58a6ff;
        margin: 0;
        padding: 0;
        display: none;
        scrollbar-size: 1 1;
    }
    #suggestion-box > .option-list--option-highlighted {
        background: #1f6feb;
        color: #ffffff;
        text-style: bold;
    }
    StatusBar {
        width: 100%;
        height: 1;
        background: #21262d;
        color: #8b949e;
        padding: 0 2;
        content-align: left middle;
    }
    """
    
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("tab", "toggle_mode", "Toggle Mode"),
        ("ctrl+k", "palette", "Command Palette"),
        ("ctrl+e", "open_editor", "Open Editor"),
        ("ctrl+y", "copy_last_response", "Copy Last Response"),
        ("pageup", "scroll_transcript_up", "Scroll Up"),
        ("pagedown", "scroll_transcript_down", "Scroll Down"),
    ]
    
    def action_copy_last_response(self):
        """Copies the latest AI message to system clipboard."""
        import subprocess
        from nexa.core.ai.memory.core import ChatMemoryManager
        mem = getattr(self.runtime, "memory", None) or getattr(self.runtime, "memory_manager", None) or ChatMemoryManager()
        last = mem.get_last_message(self.runtime.session_id)
        if last and last.get("content"):
            content = last["content"]
            try:
                if sys.platform == "win32":
                    proc = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
                    proc.communicate(input=content.encode('utf-8'))
                else:
                    proc = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
                    proc.communicate(input=content.encode('utf-8'))
                self.set_status(f"Copied {len(content)} chars to clipboard.")
            except Exception as e:
                self.set_status(f"Copy failed: {e}")
        else:
            self.set_status("Nothing to copy.")

    def on_key(self, event: events.Key) -> None:
        if event.key == "tab":
            # If a modal screen is open (e.g. ApprovalModal, SelectionModal), let Tab navigate modal controls
            if len(self.screen_stack) > 1:
                return
            event.prevent_default()
            event.stop()
            self.action_toggle_mode()

    def action_toggle_mode(self):
        """Toggle between PLAN (Read-Only analysis) and BUILD (Write & Code changes) mode."""
        curr_mode = Config.get("agent.mode", "PLAN")
        new_mode = "BUILD" if curr_mode == "PLAN" else "PLAN"
        Config.set("agent.mode", new_mode)
        if hasattr(self, "status_bar"):
            self.status_bar.mode = new_mode
        self.set_status(f"Mode switched to {new_mode}")

    def action_scroll_transcript_up(self):
        self.query_one("#transcript").scroll_up(animate=False)
        
    def action_scroll_transcript_down(self):
        self.query_one("#transcript").scroll_down(animate=False)

    def action_open_editor(self):
        """Open system external editor (Notepad, VS Code, Nano, Vim, etc.) to compose input."""
        import tempfile
        import os
        import subprocess
        import shutil

        inp = self.query_one("#prompt-input")
        initial_text = inp.value or ""

        # Determine editor
        editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")
        if not editor:
            if sys.platform == "win32":
                # Check for code (VS Code) or notepad
                if shutil.which("code"):
                    editor = "code --wait"
                else:
                    editor = "notepad.exe"
            else:
                for candidate in ["nano", "vim", "vi"]:
                    if shutil.which(candidate):
                        editor = candidate
                        break
                if not editor:
                    editor = "nano"

        try:
            with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w", encoding="utf-8") as tf:
                tf.write(initial_text)
                temp_path = tf.name

            # Run external editor
            import shlex
            def _run_sub():
                if sys.platform == "win32":
                    subprocess.run(f'{editor} "{temp_path}"', shell=True, check=False)
                else:
                    if os.path.isfile(editor):
                        cmd_parts = [editor, temp_path]
                    else:
                        cmd_parts = shlex.split(editor) + [temp_path]
                    subprocess.run(cmd_parts, check=False)

            try:
                with self.suspend():
                    _run_sub()
            except Exception:
                _run_sub()

            if os.path.exists(temp_path):
                with open(temp_path, "r", encoding="utf-8") as f:
                    new_text = f.read()
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

                new_text = new_text.strip()
                if new_text:
                    # Flatten newlines into safe spaces/multiline representation so it shows in text area
                    # and let the user inspect/edit before pressing Enter to submit
                    inp.value = new_text.replace("\r\n", " ").replace("\n", " ")
                    inp.focus()
                    inp.cursor_position = len(inp.value)
                    self.set_status("Editor content loaded into input. Press Enter to submit.")
        except Exception as e:
            self.print_to_chat(f"[!] Error opening editor: {e}")


    def __init__(self, command_handler, runtime):
        super().__init__()
        self.command_handler = command_handler
        self.runtime = runtime
        self.status_panel = StatusPanel(id="status-panel")
        
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-area"):
            with VerticalScroll(id="transcript"):
                # Initial greeting messages
                pass
            yield self.status_panel
            
        with Vertical(id="bottom-dock"):
            yield OptionList(id="suggestion-box")
            yield Input(placeholder="Nexa> _", id="prompt-input")
            self.status_bar = StatusBar()
            yield self.status_bar
        
    def on_mount(self):
        self.query_one("#prompt-input").focus()
        # Bridge the bus
        Bridge.subscribe(self.runtime.bus, "*", self)
        
        provider = Config.get("provider", "mock")
        model = Config.get(f"{provider}.model", "unknown")
        mode = Config.get("agent.mode", "PLAN")
        self.status_bar.mode = mode
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
        
        # Load and render past conversation messages if resuming a session
        self.load_session_history(self.runtime.session_id)
        
        self.set_interval(1.0, self.refresh_status_panel)

    def load_session_history(self, session_id: int):
        """Render past messages from database into the chat transcript."""
        from nexa.core.ai.memory.core import ChatMemoryManager
        mem = getattr(self.runtime, "memory", None) or getattr(self.runtime, "memory_manager", None) or ChatMemoryManager()
        try:
            past_msgs = mem.load_session_messages(session_id, limit=50)
            if past_msgs:
                for m in past_msgs:
                    role = m.get("role", "user")
                    content = m.get("content", "")
                    if role == "user":
                        self.print_to_chat(content, role="user")
                    elif role == "assistant":
                        self.print_to_chat(content, role="ai")
        except Exception:
            pass

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
        
    from nexa.commands.ai.slash_commands import SLASH_METADATA
    SLASH_COMMANDS_META = [(cmd, desc) for cmd, desc, _ in SLASH_METADATA]

    def on_input_changed(self, event: Input.Changed):
        val = event.value
        sbox = self.query_one("#suggestion-box", OptionList)
        if val.startswith("/"):
            prefix = val.lower()
            matching = [
                (cmd, desc) for cmd, desc in self.SLASH_COMMANDS_META
                if cmd.lower().startswith(prefix) or prefix == "/" or prefix in cmd.lower()
            ]
            if matching:
                sbox.clear_options()
                for cmd, desc in matching:
                    sbox.add_option(Option(f"{cmd} - {desc}", id=cmd))
                sbox.display = True
                sbox.highlighted = 0
            else:
                sbox.display = False
        else:
            sbox.display = False

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        if event.option_list.id == "suggestion-box":
            cmd = event.option.id
            sbox = self.query_one("#suggestion-box", OptionList)
            sbox.display = False
            inp = self.query_one("#prompt-input", Input)
            if cmd:
                needs_args = ["/set-api-key", "/plan", "/facts set", "/facts remove", "/unpin", "/session delete", "/rename", "/models"]
                needs_modal = ["/select-provider", "/set-model", "/sessions", "/session", "/session list", "/load", "/resume", "/continue"]
                if cmd in needs_modal:
                    inp.value = ""
                    self.handle_palette_result(cmd)
                elif cmd in needs_args:
                    inp.value = cmd + " "
                    inp.focus()
                    inp.cursor_position = len(inp.value)
                elif cmd == "/editor":
                    self.action_open_editor()
                else:
                    inp.value = ""
                    self.handle_palette_result(cmd)

    def on_input_submitted(self, event: Input.Submitted):
        sbox = self.query_one("#suggestion-box", OptionList)
        if sbox.display and sbox.highlighted is not None and len(sbox.options) > 0 and event.value.strip() == "/":
            # If user typed just "/" and pressed Enter, pick the highlighted suggestion
            chosen = sbox.get_option_at_index(sbox.highlighted)
            sbox.display = False
            if chosen and chosen.id:
                event.input.value = ""
                self.handle_palette_result(chosen.id)
                return
        sbox.display = False

        cmd = event.value.strip()
        if not cmd:
            return
            
        event.input.value = ""
        
        # Open command palette directly if user just types "/"
        if cmd == "/":
            self.action_palette()
            return
            
        # Open external editor if user types /editor
        if cmd.lower() == "/editor":
            self.action_open_editor()
            return
            
        needs_args_or_modal = [
            "/select-provider", "/set-model", "/set-api-key", "/load", "/plan", 
            "/facts set", "/facts remove", "/unpin", "/session", "/sessions", 
            "/session list", "/session enter", "/session delete", "/resume", "/continue"
        ]
        
        # If user types exactly the command without args, trigger the palette handler (which shows modal or prepopulates input)
        if cmd in needs_args_or_modal:
            self.handle_palette_result(cmd)
            return
            
        # Handle UI-based API key prompting for /select-provider <provider>
        if cmd.lower().startswith("/select-provider "):
            parts = cmd.split()
            if len(parts) == 2:
                prov = parts[1].lower()
                if prov in ["deepseek", "groq", "gemini"]:
                    api_key = Config.get(f"{prov}.api_key", "")
                    if not api_key:
                        def _handle_key(key):
                            if key:
                                Config.set(f"{prov}.api_key", key)
                            self.status_bar.status_text = "Processing..."
                            self.run_command(cmd)
                        self.push_screen(InputModal(f"Enter API Key for {prov}:", password=True), _handle_key)
                        return
                        
        # Handle UI-based API key prompting for /set-api-key <provider>
        if cmd.lower().startswith("/set-api-key "):
            parts = cmd.split()
            if len(parts) == 2:
                prov = parts[1].lower()
                def _handle_key_set(key):
                    if key:
                        self.status_bar.status_text = "Processing..."
                        self.run_command(f"{parts[0]} {prov} {key}")
                self.push_screen(InputModal(f"Enter API Key for {prov}:", password=True), _handle_key_set)
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

    def safe_invoke(self, func, *args, **kwargs):
        import threading
        if threading.get_ident() == getattr(self, "_thread_id", None):
            func(*args, **kwargs)
        else:
            self.call_from_thread(func, *args, **kwargs)

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
            self.safe_invoke(self.status_panel.add_process, self._human_event(ctx), self._status_of(ctx))
            return

        if ctx.event_name == "AgentLoopIteration":
            iter_num = payload.get("iteration", 0)
            max_iter = payload.get("max_iterations", 15)
            self.safe_invoke(self.status_panel.add_process, f"Agent Loop [{iter_num}/{max_iter}]", "running")
            return
            
        if ctx.event_name == "UI_Print":
            msg = ctx.payload.get("message", "")
            role = ctx.payload.get("role", "ai")
            self.safe_invoke(self.print_to_chat, msg, role)
            return

        if ctx.event_name == "ToolCalled":
            tool_name = payload.get("tool_name", "Tool")
            status = payload.get("status", "running")
            self.safe_invoke(self.status_panel.add_process, tool_name, status)
            return

        if ctx.event_name == "AgentTasksUpdated":
            tasks = payload.get("tasks", [])
            self.safe_invoke(self.status_panel.set_agent_tasks, tasks)
            return

            
        if ctx.event_name in ("AfterPlanning", "BeforeApproval"):
            if ctx.event_name == "AfterPlanning":
                self.status_panel.add_process("Planning complete", "ok")
            plan = payload.get("plan")
            work_items = (getattr(plan, "work_items", [])
                          if not isinstance(plan, dict)
                          else plan.get("work_items", []))
            if work_items:
                self.safe_invoke(self.status_panel.set_todos, work_items)

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

            if cmd in ["/sessions", "/session", "/session list", "/load", "/resume", "/continue"]:
                from nexa.core.ai.memory.core import ChatMemoryManager
                mem = getattr(self.runtime, "memory_manager", None) or getattr(self.runtime, "memory", None) or ChatMemoryManager()
                def _handle_session_choice(result):
                    if result and isinstance(result, tuple) and len(result) == 2:
                        action, sid = result
                        if action == "select":
                            self.runtime.session_id = sid
                            self.status_bar.status_text = f"Loaded Session #{sid}"
                            self.print_to_chat(f"[*] Loaded chat session #{sid}", role="ai")
                            self.load_session_history(sid)
                self.push_screen(SessionSelectionModal(mem, self.runtime.cwd, self.runtime.session_id), _handle_session_choice)
                return

            needs_args = ["/set-api-key", "/plan", "/facts set", "/facts remove", "/unpin", "/session delete", "/rename", "/models"]
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
