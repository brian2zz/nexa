from textual.containers import VerticalScroll
from textual.widgets import Static, RichLog

PROVIDER_RATES = {
    "deepseek": (0.27, 1.10),
    "groq":     (0.30, 0.60),
    "ollama":   (0.0, 0.0),
}

class StatusPanel(VerticalScroll):
    DEFAULT_CSS = """
    StatusPanel {
        background: $surface;
        padding: 0 1;
    }
    .status-header {
        text-style: bold;
        color: $accent;
        padding-bottom: 1;
        border-bottom: solid $primary;
    }
    .status-section {
        text-style: bold;
        color: $text;
        margin-top: 1;
    }
    .status-info {
        color: $text-muted;
    }
    .status-todo-done {
        color: $success;
    }
    .status-todo-pending {
        color: $text;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._prompt_total = 0
        self._completion_total = 0
        self.PROMPT_RATE = 0.0
        self.COMPLETION_RATE = 0.0

    def compose(self):
        yield Static("🖥 Nexa Status", classes="status-header", id="status-header")
        yield Static("", classes="status-info", id="status-info")
        yield Static("📊 Context & Token", classes="status-section")
        yield Static("Prompt: 0 · Output: 0 · Total: 0", id="status-tokens")
        yield Static("Cost: $0.0000", id="status-cost")
        yield Static("📋 Todo", classes="status-section")
        yield VerticalScroll(id="status-todo-list", classes="status-info")
        yield Static("⚙ Proses", classes="status-section")
        yield RichLog(id="status-process-log", wrap=True, highlight=True)

    def set_info(self, *, version: str, project_path: str,
                 provider: str, model: str, session_id):
        """Isi blok info."""
        self.query_one("#status-info", Static).update(
            f"Version : {version}\n"
            f"Path    : {project_path}\n"
            f"Provider: {provider}\n"
            f"Model   : {model}\n"
            f"Session : {session_id}"
        )

    def set_provider_rates(self, provider: str):
        self.PROMPT_RATE, self.COMPLETION_RATE = PROVIDER_RATES.get(provider, (0.0, 0.0))

    def update_tokens(self, prompt_tokens: int, completion_tokens: int):
        """Akumulasi token per sesi lalu re-render."""
        self._prompt_total += prompt_tokens
        self._completion_total += completion_tokens
        total = self._prompt_total + self._completion_total
        self.query_one("#status-tokens", Static).update(
            f"Prompt: {self._prompt_total:,} · Output: {self._completion_total:,} · Total: {total:,}"
        )
        self.query_one("#status-cost", Static).update(f"Cost: {self.estimate_cost():.4f} USD")

    def estimate_cost(self) -> float:
        """Estimasi biaya."""
        return (
            self._prompt_total * self.PROMPT_RATE
            + self._completion_total * self.COMPLETION_RATE
        ) / 1_000_000

    def set_todos(self, work_items):
        """Render checklist todo dari plan."""
        container = self.query_one("#status-todo-list", VerticalScroll)
        container.remove_children()
        for i, w in enumerate(work_items, 1):
            title = w.title if hasattr(w, "title") else w.get("title", "")
            affected = getattr(w, "affected_files", []) or w.get("affected_files", [])
            files = ", ".join(affected[:3])
            label = f"☐ [{i}] {title}"
            if files:
                label += f"  ( {files} )"
            container.mount(Static(label, classes="status-todo-pending", id=f"todo-{i}"))

    def add_process(self, text: str, status: str = "info"):
        """Tulis satu baris ke log proses."""
        icon = {"ok": "✅", "err": "❌", "running": "⏳", "info": "•"}.get(status, "•")
        self.query_one("#status-process-log", RichLog).write(f"{icon} {text}")

    def log_tool(self, tool_name: str, status: str = "running"):
        """Kompatibel dengan ToolPanel lama."""
        mapping = {"running": "running", "success": "ok", "error": "err"}
        self.add_process(tool_name, mapping.get(status, "info"))
