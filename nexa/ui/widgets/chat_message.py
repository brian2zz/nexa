from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Collapsible, Markdown, Static, RichLog
from textual.reactive import reactive

class ChatMessage(Vertical):
    """
    Sebuah komponen pesan chat yang memiliki bagian:
    1. Header (User/AI label)
    2. Collapsible (untuk menampung proses reasoning/thought)
    3. Markdown (untuk hasil LLM akhir) atau sekadar RichLog untuk command output
    """
    DEFAULT_CSS = """
    ChatMessage {
        width: 100%;
        height: auto;
        padding: 1;
        margin-bottom: 1;
        border-bottom: solid $surface-lighten-1;
    }
    
    .chat-user {
        color: $primary;
        text-style: bold;
    }
    
    .chat-ai {
        color: $success;
        text-style: bold;
    }
    
    #message-thought-container {
        display: none; /* Sembunyikan secara default jika kosong */
        margin-bottom: 1;
        border: solid $surface;
    }
    
    #message-thought-log {
        height: 5;
        background: $surface;
        color: $text-muted;
    }
    """
    
    def __init__(self, role: str, text: str = "", **kwargs):
        super().__init__(**kwargs)
        self.role = role
        self._text_buffer = text
        self.is_thinking = False
        self._last_thought = ""
        self.markdown = Markdown(self._text_buffer)
        
    def compose(self) -> ComposeResult:
        role_label = "🧑 User" if self.role == "user" else "🤖 Nexa"
        role_class = "chat-user" if self.role == "user" else "chat-ai"
        
        yield Static(role_label, classes=role_class)
        
        with Collapsible(title="💭 Processes", id="message-thought-container", collapsed=True):
            yield RichLog(id="message-thought-log", wrap=True)
            
        yield self.markdown
        
    def add_thought(self, text: str):
        """Menambahkan log proses (seperti classfiying intent) ke dalam Collapsible."""
        if text == self._last_thought:
            return
        self._last_thought = text
        
        container = self.query_one("#message-thought-container")
        container.styles.display = "block" # Munculkan
        log = self.query_one("#message-thought-log", RichLog)
        log.write(text)
        
    def append_text(self, text: str):
        """Menambahkan teks hasil LLM."""
        self._text_buffer += text
        # Memperbarui markdown secara langsung
        self.markdown.update(self._text_buffer)
        
    def finish(self):
        """Tandai selesai."""
        self.is_thinking = False
