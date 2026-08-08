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
        width: 60%;
        height: auto;
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
    }
    
    #approval-comment {
        margin-top: 1;
        display: none;
    }
    
    #approval-markdown-scroll {
        height: 1fr;
        border: solid green;
        margin: 1 0;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    def __init__(self, context: EventContext, **kwargs):
        super().__init__(**kwargs)
        self.event_context = context
        self.plan = context.payload.get("plan", {})
        
    def compose(self) -> ComposeResult:
        with Vertical(id="approval-dialog"):
            yield Static("⚠️ Approval Required for Execution Plan", id="approval-title")
            
            with VerticalScroll(id="approval-markdown-scroll"):
                try:
                    # If it's a PlanningResult, try to get its markdown
                    if hasattr(self.plan, "to_markdown"):
                        md_content = self.plan.to_markdown()
                    elif isinstance(self.plan, dict):
                        md_content = "```json\n" + str(self.plan) + "\n```"
                    else:
                        md_content = str(self.plan)
                except Exception:
                    md_content = "Failed to render plan details."
                    
                yield Markdown(md_content)
            
            with Horizontal(id="approval-buttons"):
                yield Button("Yes, Execute", variant="success", id="btn-yes")
                yield Button("No, Abort", variant="error", id="btn-no")
                yield Button("Provide Feedback (C)", variant="primary", id="btn-comment")
                
            yield Input(placeholder="Type your feedback here and press Enter...", id="approval-comment")

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
