from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import OptionList
from textual.widgets.option_list import Option

class CommandPaletteModal(ModalScreen[str]):
    """
    Modal screen for quick command selection (Ctrl+K).
    Returns the selected command string.
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]
    
    CSS = """
    CommandPaletteModal {
        align: center middle;
        background: rgba(13, 17, 23, 0.85);
    }
    
    #palette-list {
        width: 60%;
        height: 60%;
        border: round #58a6ff;
        background: #161b22;
        padding: 1;
    }
    """
    
    def compose(self) -> ComposeResult:
        from nexa.commands.ai.slash_commands import SLASH_METADATA
        options = [
            Option(f"{cmd} - {desc}", id=cmd) for cmd, desc, _ in SLASH_METADATA
        ]
        yield OptionList(*options, id="palette-list")

    def on_key(self, event) -> None:
        if event.key == "escape":
            event.prevent_default()
            event.stop()
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)
        
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        cmd = event.option.id
        if cmd:
            self.dismiss(cmd)

class GenericSelectionModal(ModalScreen[str]):
    """Generic modal screen to present a list of options."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]
    
    CSS = """
    GenericSelectionModal {
        align: center middle;
        background: rgba(13, 17, 23, 0.85);
    }
    
    #selection-title {
        width: 60%;
        color: #58a6ff;
        text-style: bold;
        padding-bottom: 1;
        content-align: center middle;
    }
    
    #selection-list {
        width: 60%;
        height: 60%;
        border: round #58a6ff;
        background: #161b22;
        padding: 1;
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

    def on_key(self, event) -> None:
        if event.key == "escape":
            event.prevent_default()
            event.stop()
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)
        
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        val = event.option.id
        if val:
            self.dismiss(val)

class SessionSelectionModal(ModalScreen[tuple]):
    """Interactive Session Selection Modal with DEL key support to delete sessions."""

    CSS = """
    SessionSelectionModal {
        align: center middle;
        background: rgba(13, 17, 23, 0.85);
    }

    #session-modal-title {
        width: 70%;
        color: #58a6ff;
        text-style: bold;
        padding-bottom: 0;
        content-align: center middle;
    }

    #session-modal-subtitle {
        width: 70%;
        color: #8b949e;
        padding-bottom: 1;
        content-align: center middle;
    }

    #session-list {
        width: 70%;
        height: 65%;
        border: round #58a6ff;
        background: #161b22;
        padding: 1;
    }
    """

    BINDINGS = [
        ("delete", "delete_session", "Delete"),
        ("backspace", "delete_session", "Delete"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, memory_manager, project_path: str, current_session_id: int, **kwargs):
        super().__init__(**kwargs)
        self.memory_manager = memory_manager
        self.project_path = project_path
        self.current_session_id = current_session_id

    def compose(self) -> ComposeResult:
        from textual.widgets import Label
        yield Label("💬 Select Chat Session", id="session-modal-title")
        yield Label("[Enter] Select / Resume  •  [DEL / Backspace] Delete Session  •  [ESC] Cancel", id="session-modal-subtitle")
        yield OptionList(id="session-list")

    def on_mount(self) -> None:
        self.refresh_session_list()

    def refresh_session_list(self) -> None:
        olist = self.query_one("#session-list", OptionList)
        olist.clear_options()
        sessions = self.memory_manager.get_project_sessions(self.project_path, limit=20)
        if not sessions:
            olist.add_option(Option("No past sessions found. (Press ESC to close)", id="none"))
            return

        for sid, created_at, msg_count, name in sessions:
            dt_str = str(created_at).split('.')[0] if created_at else ""
            title = name if name else f"Session #{sid}"
            active_badge = " [Active]" if sid == self.current_session_id else ""
            display_text = f"#{sid} | {title} ({msg_count} msgs) - {dt_str}{active_badge}"
            olist.add_option(Option(display_text, id=str(sid)))

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        val = event.option.id
        if val and val != "none":
            self.dismiss(("select", int(val)))

    def action_delete_session(self) -> None:
        olist = self.query_one("#session-list", OptionList)
        if olist.highlighted is not None and len(olist.options) > 0:
            opt = olist.get_option_at_index(olist.highlighted)
            if opt and opt.id and opt.id != "none":
                sid = int(opt.id)
                self.memory_manager.delete_session(sid)
                self.refresh_session_list()

    def action_cancel(self) -> None:
        self.dismiss(None)

class InputModal(ModalScreen[str]):
    """Modal screen for text input (e.g. API keys)."""
    
    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    CSS = """
    InputModal {
        align: center middle;
        background: rgba(13, 17, 23, 0.85);
    }
    
    #input-container {
        width: 60%;
        height: auto;
        padding: 1 2;
        border: thick #58a6ff;
        background: #161b22;
    }
    #modal-input-title {
        color: #58a6ff;
        text-style: bold;
        padding-bottom: 0;
    }
    #modal-input-hint {
        color: #8b949e;
        padding-bottom: 1;
    }
    """
    
    def __init__(self, title: str, password: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.title_text = title
        self.is_password = password
        
    def compose(self) -> ComposeResult:
        from textual.containers import Vertical
        from textual.widgets import Label, Input
        with Vertical(id="input-container"):
            yield Label(self.title_text, id="modal-input-title")
            yield Label("[Enter] Submit  •  [ESC] Cancel / Close", id="modal-input-hint")
            yield Input(password=self.is_password, id="modal-input")
            
    def on_mount(self):
        self.query_one("#modal-input").focus()

    def on_key(self, event) -> None:
        if event.key == "escape":
            event.prevent_default()
            event.stop()
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)
        
    def on_input_submitted(self, event) -> None:
        val = event.value.strip()
        if val:
            self.dismiss(val)
        else:
            self.dismiss(None)
