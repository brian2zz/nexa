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
            Option("/help - Show available commands", id="/help"),
            Option("/status - Show runtime status", id="/status"),
            Option("/plan - Generate an Execution Plan for a task", id="/plan"),
            Option("/commands - Show CLI commands for this project", id="/commands"),
            Option("/history - Show chat session history", id="/history"),
            Option("/session list - Show all chat sessions", id="/session list"),
            Option("/load - Load a past chat session", id="/load"),
            Option("/clear - Clear current chat session", id="/clear"),
            Option("/select-provider - Switch AI Provider", id="/select-provider"),
            Option("/set-model - Set active model for provider", id="/set-model"),
            Option("/set-api-key - Set API Key for provider", id="/set-api-key"),
            Option("/facts - Show project facts", id="/facts"),
            Option("/pins - Show pinned memory", id="/pins"),
            Option("/pin - Pin last AI response", id="/pin"),
            Option("/clearpins - Clear all pinned memory", id="/clearpins"),
            Option("/exit - Quit the application", id="/exit"),
            id="palette-list"
        )
        
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        cmd = event.option.id
        if cmd:
            self.dismiss(cmd)

class GenericSelectionModal(ModalScreen[str]):
    """Generic modal screen to present a list of options."""
    
    CSS = """
    GenericSelectionModal {
        align: center middle;
        background: $background 80%;
    }
    
    #selection-list {
        width: 50%;
        height: 50%;
        border: thick $primary;
        background: $surface;
    }
    """
    
    def __init__(self, title: str, options: list[tuple[str, str]], **kwargs):
        super().__init__(**kwargs)
        self.title_text = title
        self.options_data = options
        
    def compose(self) -> ComposeResult:
        from textual.widgets import Label
        yield Label(self.title_text, id="selection-title")
        opts = [Option(desc, id=val) for val, desc in self.options_data]
        yield OptionList(*opts, id="selection-list")
        
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        val = event.option.id
        if val:
            self.dismiss(val)

