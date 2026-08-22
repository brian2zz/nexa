import sys
import pytest
from nexa.core.events.bus import PipelineBus
from nexa.core.models.enums import EventPriority
from nexa.core.models.events import EventContext
from nexa.ui.app import NexaApp
from textual.widgets import OptionList
from nexa.ui.screens.approval import ApprovalModal
from nexa.ui.screens.palette import CommandPaletteModal, SessionSelectionModal
from nexa.ui.screens.clarification import ClarificationModal


class FakeRuntime:
    def __init__(self):
        self.bus = PipelineBus(max_workers=2)
        self.session_id = "test-session"

    def __getattr__(self, name):
        return None


def make_handler():
    def handler(cmd):
        print(f"cmd={cmd}")
        return True
    return handler


def make_app():
    return NexaApp(make_handler(), FakeRuntime())


def event(name, payload=None, session="s"):
    return EventContext(
        event_name=name,
        timestamp="2026-08-08",
        source="test",
        priority=EventPriority.NORMAL,
        session_id=session,
        payload=payload,
    )


@pytest.mark.asyncio
async def test_tui_mounts_and_submits_command():
    app = make_app()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        assert app.query_one("#prompt-input") is not None
        assert app.query_one("#transcript") is not None
        assert app.query_one("#status-panel") is not None
        # Submit a command through the input
        await pilot.press("h", "i", "enter")
        await pilot.pause()
        await pilot.pause()
        await pilot.pause()
        transcript = app.query_one("#transcript")
        messages = app.query("ChatMessage")
        text = "\n".join(msg._text_buffer for msg in messages)
        assert "cmd=hi" in text
        assert app.status_bar.status_text == "Ready"


@pytest.mark.asyncio
async def test_tool_called_updates_panel():
    app = make_app()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        # Status panel is always visible (no toggle needed)
        app.runtime.bus.publish(event("ToolCalled", {"tool_name": "grep_search", "status": "running"}))
        await pilot.pause()
        await pilot.pause()
        log = app.query_one("#status-process-log")
        text = "".join(strip.text for strip in log.lines)
        assert "grep_search" in text


@pytest.mark.asyncio
async def test_before_approval_pushes_modal():
    app = make_app()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        app.runtime.bus.publish(event("BeforeApproval", {"plan": {"objective": "test"}}))
        await pilot.pause()
        assert any(isinstance(s, ApprovalModal) for s in app.screen_stack)
        # Dismiss modal with No, Abort
        await pilot.press("tab")
        await pilot.press("enter")
        await pilot.pause()


@pytest.mark.asyncio
async def test_before_approval_yes_publishes_approval_granted():
    app = make_app()
    granted = []
    app.runtime.bus.subscribe("ApprovalGranted", lambda ctx: granted.append(ctx))
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        app.runtime.bus.publish(event("BeforeApproval", {"plan": {"objective": "test"}}))
        await pilot.pause()
        await pilot.pause()
        await pilot.click("#btn-yes")
        await pilot.pause()
        await pilot.pause()
        assert len(granted) == 1


@pytest.mark.asyncio
async def test_palette_opens_and_executes():
    app = make_app()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        app.action_palette()
        await pilot.pause()
        assert any(isinstance(s, CommandPaletteModal) for s in app.screen_stack)


@pytest.mark.asyncio
async def test_editor_action_and_input(monkeypatch, tmp_path):
    app = make_app()
    fake_editor = tmp_path / "fake_editor.py"
    fake_editor.write_text(
        "import sys\n"
        "with open(sys.argv[1], 'w', encoding='utf-8') as f:\n"
        "    f.write('Hello from external editor!\\nSecond line')\n"
    )
    monkeypatch.setenv("EDITOR", f'"{sys.executable}" "{fake_editor.as_posix()}"')

    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        inp = app.query_one("#prompt-input")
        app.action_open_editor()
        await pilot.pause()
        # Text is loaded into input box ready for user inspection/edit
        assert "Hello from external editor! Second line" in inp.value


@pytest.mark.asyncio
async def test_slash_input_shows_suggestion_box():
    app = make_app()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        sbox = app.query_one("#suggestion-box", OptionList)
        assert sbox.display is False

        # Type /
        await pilot.press("slash")
        await pilot.pause()
        assert sbox.display is True
        assert len(sbox.options) > 0

        # Type 'ed'
        await pilot.press("e", "d")
        await pilot.pause()
        assert sbox.display is True
        assert any("/editor" in str(opt.prompt) for opt in sbox.options)

        # Backspace until empty
        await pilot.press("backspace", "backspace", "backspace")
        await pilot.pause()
        assert sbox.display is False


@pytest.mark.asyncio
async def test_tab_toggles_plan_and_build_mode():
    from nexa.config import Config
    Config.set("agent.mode", "PLAN")
    app = make_app()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        assert app.status_bar.mode == "PLAN"
        
        # Press Tab -> Toggle to BUILD
        await pilot.press("tab")
        await pilot.pause()
        assert app.status_bar.mode == "BUILD"
        
        # Press Tab -> Toggle back to PLAN
        await pilot.press("tab")
        await pilot.pause()
        assert app.status_bar.mode == "PLAN"


@pytest.mark.asyncio
async def test_status_panel_always_visible():
    app = make_app()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        assert not app.status_panel.display is False
        assert app.query_one("#status-panel") is not None
        # Info block should be populated from runtime/Config
        info = app.query_one("#status-info")
        assert "Version" in str(info.render())


@pytest.mark.asyncio
async def test_clarification_requested_pushes_modal():
    app = make_app()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        app.runtime.bus.publish(event("ClarificationRequested", {"questions": [
            {"key": "file_path", "question": "File mana?", "hint": "modules/x"},
        ]}))
        await pilot.pause()
        assert any(isinstance(s, ClarificationModal) for s in app.screen_stack)


@pytest.mark.asyncio
async def test_clarification_modal_renders_questions():
    app = make_app()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        app.runtime.bus.publish(event("ClarificationRequested", {"questions": [
            {"key": "file_path", "question": "File mana?", "hint": "modules/x"},
            {"key": "style", "question": "Gaya?", "hint": ""},
        ]}))
        await pilot.pause()
        modal = next(s for s in app.screen_stack if isinstance(s, ClarificationModal))
        assert modal.query_one("#input-file_path") is not None
        assert modal.query_one("#input-style") is not None


@pytest.mark.asyncio
async def test_clarification_submit_publishes_answered():
    app = make_app()
    answered = []
    app.runtime.bus.subscribe(
        "ClarificationAnswered",
        lambda ctx: answered.append(ctx.payload.get("answers")),
    )
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        app.runtime.bus.publish(event("ClarificationRequested", {"questions": [
            {"key": "file_path", "question": "File mana?", "hint": "modules/x"},
        ]}))
        await pilot.pause()
        from textual.widgets import Input
        modal = next(s for s in app.screen_stack if isinstance(s, ClarificationModal))
        modal.query_one("#input-file_path", Input).value = "modules/x"
        modal.query_one("#btn-submit").press()
        await pilot.pause()
        await pilot.pause()
        assert answered and answered[-1] == {"file_path": "modules/x"}


@pytest.mark.asyncio
async def test_clarification_empty_submit_publishes_empty_and_pops():
    app = make_app()
    answered = []
    app.runtime.bus.subscribe(
        "ClarificationAnswered",
        lambda ctx: answered.append(ctx.payload.get("answers")),
    )
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        app.runtime.bus.publish(event("ClarificationRequested", {"questions": [
            {"key": "file_path", "question": "File mana?", "hint": "modules/x"},
        ]}))
        await pilot.pause()
        modal = next(s for s in app.screen_stack if isinstance(s, ClarificationModal))
        modal.query_one("#btn-submit").press()
        await pilot.pause()
        await pilot.pause()
        assert answered and answered[-1] == {}
        assert not any(isinstance(s, ClarificationModal) for s in app.screen_stack)


@pytest.mark.asyncio
async def test_clarification_skip_publishes_empty_and_pops():
    app = make_app()
    answered = []
    app.runtime.bus.subscribe(
        "ClarificationAnswered",
        lambda ctx: answered.append(ctx.payload.get("answers")),
    )
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        app.runtime.bus.publish(event("ClarificationRequested", {"questions": [
            {"key": "file_path", "question": "File mana?", "hint": "modules/x"},
        ]}))
        await pilot.pause()
        modal = next(s for s in app.screen_stack if isinstance(s, ClarificationModal))
        modal.query_one("#btn-skip").press()
        await pilot.pause()
        await pilot.pause()
        assert answered and answered[-1] == {}
        assert not any(isinstance(s, ClarificationModal) for s in app.screen_stack)


@pytest.mark.asyncio
async def test_session_modal_popup_and_delete():
    from nexa.core.ai.memory.core import ChatMemoryManager
    mem = ChatMemoryManager()
    sid = mem.create_session("test_proj")
    mem.save_message(sid, "user", "Hello first session")
    
    app = make_app()
    app.runtime.memory_manager = mem
    app.runtime.cwd = "test_proj"
    
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        # Trigger /sessions
        app.handle_palette_result("/sessions")
        await pilot.pause()
        assert any(isinstance(s, SessionSelectionModal) for s in app.screen_stack)
        
        modal = next(s for s in app.screen_stack if isinstance(s, SessionSelectionModal))
        olist = modal.query_one("#session-list", OptionList)
        assert len(olist.options) > 0
        
        # Press Delete -> Deletes highlighted session
        await pilot.press("delete")
        await pilot.pause()


@pytest.mark.asyncio
async def test_theme_applied_on_mount():
    from nexa.config import Config
    Config.set("ui.theme", "nord")
    app = make_app()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        assert app.theme == "nord"

    Config.set("ui.theme", "dark")
    app2 = make_app()
    async with app2.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        assert app2.theme == "textual-dark"


@pytest.mark.asyncio
async def test_theme_selection_modal_applies_live():
    from nexa.ui.screens.palette import GenericSelectionModal
    app = make_app()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        app.handle_palette_result("/themes")
        await pilot.pause()
        assert any(isinstance(s, GenericSelectionModal) for s in app.screen_stack)
        modal = next(s for s in app.screen_stack if isinstance(s, GenericSelectionModal))
        # Pick 'nord' option
        olist = modal.query_one("#selection-list", OptionList)
        olist.highlighted = 1  # 0 is dark, 1 is nord
        await pilot.press("enter")
        await pilot.pause()
        await pilot.pause()
        assert app.theme == "nord"

