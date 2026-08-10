from typing import Dict, List, Any
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Static, Input
from textual.containers import Vertical, Horizontal, VerticalScroll

class ClarificationModal(ModalScreen[dict]):
    """
    Modal screen to ask clarification questions before AI Planning.
    Returns a dict mapping question keys to the user's answers.
    """
    
    CSS = """
    ClarificationModal {
        align: center middle;
        background: $background 80%;
    }
    
    #clarification-dialog {
        padding: 1 2;
        width: 60%;
        height: auto;
        border: thick $warning;
        background: $surface;
    }
    
    #clarification-title {
        text-align: center;
        text-style: bold;
        color: $warning;
        padding-bottom: 1;
        border-bottom: solid $primary;
    }
    
    .clarification-question-box {
        margin: 1 0;
    }
    
    .question-label {
        text-style: bold;
        margin-bottom: 1;
    }
    
    .question-hint {
        color: $text-muted;
        text-style: italic;
        margin-bottom: 1;
    }
    
    #clarification-buttons {
        align: center middle;
        height: 3;
        margin-top: 1;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    def __init__(self, questions: List[Dict[str, Any]], **kwargs):
        super().__init__(**kwargs)
        self.questions = questions
        
    def compose(self) -> ComposeResult:
        with Vertical(id="clarification-dialog"):
            yield Static("⚠️ Nexa membutuhkan klarifikasi", id="clarification-title")
            yield Static("Saya menemukan beberapa informasi yang perlu diperjelas agar tidak salah mengeksekusi perintah Anda.", classes="question-hint")
            
            with VerticalScroll(id="clarification-scroll"):
                for q in self.questions:
                    with Vertical(classes="clarification-question-box"):
                        yield Static(q.get("question", ""), classes="question-label")
                        if q.get("hint"):
                            yield Static(f"Contoh: {q['hint']}", classes="question-hint")
                        yield Input(placeholder="Jawaban Anda...", id=f"input-{q['key']}")
            
            with Horizontal(id="clarification-buttons"):
                yield Button("Kirim Jawaban", variant="success", id="btn-submit")
                yield Button("Lewati", variant="primary", id="btn-skip")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-submit":
            answers = {}
            for q in self.questions:
                key = q["key"]
                input_widget = self.query_one(f"#input-{key}", Input)
                val = input_widget.value.strip()
                if val:
                    answers[key] = val
            self.dismiss(answers)
        elif event.button.id == "btn-skip":
            self.dismiss({})
