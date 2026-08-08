from textual.app import ComposeResult
from textual.widgets import Static, RichLog
from textual.containers import VerticalScroll
from textual.reactive import reactive

class ToolPanel(Static):
    """A collapsible right panel to show tool executions and evidence."""
    
    is_open = reactive(False)
        
    def watch_is_open(self, is_open: bool) -> None:
        self.display = is_open

    def compose(self) -> ComposeResult:
        yield Static("🔧 Tools & Evidence", id="tool-panel-header")
        yield RichLog(id="tool-panel-log", wrap=True, markup=True)
            
    def on_mount(self):
        self.display = self.is_open
        self.query_one("#tool-panel-log", RichLog).write("No tools executed yet.")
        
    def log_tool(self, tool_name: str, status: str = "running"):
        try:
            log_widget = self.query_one("#tool-panel-log", RichLog)
            icon = "⏳" if status == "running" else "✅" if status == "success" else "❌"
            line = f"{icon} {tool_name}"
            log_widget.write(line)
        except Exception:
            pass
