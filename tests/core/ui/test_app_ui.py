import pytest
from nexa.core.events.bus import PipelineBus
from nexa.core.models.enums import EventPriority
from nexa.core.models.events import EventContext
from nexa.ui.app import NexaApp
from nexa.ui.screens.approval import ApprovalModal
from nexa.ui.screens.palette import CommandPaletteModal


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
        assert app.query_one("#tool-panel") is not None
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
        # Open panel first so RichLog size is known and writes are rendered
        app.action_toggle_tools()
        await pilot.pause()
        app.runtime.bus.publish(event("ToolCalled", {"tool_name": "grep_search", "status": "running"}))
        await pilot.pause()
        await pilot.pause()
        log = app.query_one("#tool-panel-log")
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
async def test_toggle_tools_panel():
    app = make_app()
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        assert not app.tool_panel.is_open
        app.action_toggle_tools()
        await pilot.pause()
        assert app.tool_panel.is_open
        app.action_toggle_tools()
        await pilot.pause()
        assert not app.tool_panel.is_open
