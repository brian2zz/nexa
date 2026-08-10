import pytest
from nexa.core.events.bus import PipelineBus
from nexa.core.models.enums import EventPriority
from nexa.core.models.events import EventContext
from nexa.ui.app import NexaApp
from nexa.ui.screens.approval import ApprovalModal
from nexa.ui.screens.palette import CommandPaletteModal
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
        # Tab to focus first button, then press Enter (Yes, Execute)
        await pilot.press("tab")
        await pilot.pause()
        await pilot.press("enter")
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
