from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import OptionList
from textual.widgets.option_list import Option

class CommandPaletteModal(ModalScreen[str]):
    """
    Modal screen for quick command selection (Ctrl+K).
    Returns the selected command string.
    """
    
    CSS = """
    CommandPaletteModal {
        align: center middle;
        background: $background 80%;
    }
    
    #palette-list {
        width: 50%;
        height: 50%;
        border: thick $primary;
        background: $surface;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield OptionList(
            Option("/status - Show runtime status", id="/status"),
            Option("/help - Show available commands", id="/help"),
            Option("/select-provider - Change LLM provider", id="/select-provider"),
            Option("/clear - Clear chat history", id="/clear"),
            Option("/exit - Quit the application", id="/exit"),
            id="palette-list"
        )
        
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        cmd = event.option.id
        if cmd:
            self.dismiss(cmd)
