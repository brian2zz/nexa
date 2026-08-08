import contextlib
import threading
import sys
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import Input, Static, Header, RichLog
from textual import work
from nexa.ui.bridge import Bridge, BusMessage
from textual.reactive import reactive
from nexa.ui.widgets.tool_panel import ToolPanel
from nexa.ui.screens.approval import ApprovalModal
from nexa.ui.screens.palette import CommandPaletteModal
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

class NexaApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    #transcript {
        height: 1fr;
        padding: 1;
        border: solid $surface;
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
    #tool-panel {
        width: 30%;
        border-left: solid $primary;
        display: none;
    }
    #tool-panel.-open {
        display: block;
    }
    """
    
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+k", "palette", "Command Palette"),
        ("f", "toggle_tools", "Toggle Tools"),
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
        self.tool_panel = ToolPanel(id="tool-panel")
        
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with VerticalScroll(id="transcript"):
                # Initial greeting messages
                pass
            yield self.tool_panel
            
        self.status_bar = StatusBar()
        yield self.status_bar
        yield Input(placeholder="Nexa> _", id="prompt-input")
        
    def on_mount(self):
        self.query_one("#prompt-input").focus()
        # Bridge the bus
        Bridge.subscribe(self.runtime.bus, "*", self)
        
        # Override Textual's dummy stdout with our RedirectedStdout
        self.original_stdout = sys.stdout
        sys.stdout = RedirectedStdout(self)
        
        self.current_ai_msg = None
        
        self.print_to_chat("Welcome to Nexa AI Interactive Shell (TUI).\nType /help for available commands or /exit to quit.", role="ai")
        
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
        cmd = event.value
        event.input.value = ""
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
        
    def on_bus_message(self, message: BusMessage):
        ctx = message.event_context
        payload = ctx.payload or {}
        
        if ctx.event_name == "ToolCalled":
            tool_name = payload.get("tool_name", "unknown")
            status = payload.get("status", "running")
            self.tool_panel.log_tool(tool_name, status)
            
        elif ctx.event_name == "BeforeApproval":
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
            
    def action_toggle_tools(self) -> None:
        """Toggle ToolPanel with F key"""
        self.tool_panel.is_open = not self.tool_panel.is_open
        if self.tool_panel.is_open:
            self.tool_panel.add_class("-open")
        else:
            self.tool_panel.remove_class("-open")
            
    def action_palette(self) -> None:
        """Show Command Palette with Ctrl+K"""
        def handle_palette_result(cmd):
            if cmd:
                # Execute the command
                self.print_to_chat(cmd, role="user")
                self.status_bar.status_text = "Processing..."
                self.run_command(cmd)
                
        self.push_screen(CommandPaletteModal(), handle_palette_result)
