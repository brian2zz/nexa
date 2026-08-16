import pytest
import os
import sys
from nexa.commands.ai.slash_commands import SLASH_METADATA, SLASH_ALIASES, SlashCommandHandler
from nexa.commands.ai.shell import load_agents_instructions
from nexa.core.events.bus import PipelineBus

class MockRuntime:
    def __init__(self):
        self.session_id = 1
        self.bus = PipelineBus(max_workers=1)

class MockMemory:
    def __init__(self):
        self.sessions = {1: "Default Session"}
        self.messages = [{ "role": "user", "content": "hello" }]

    def rename_session(self, sid, name):
        self.sessions[sid] = name
        return True

    def load_session_messages(self, sid, limit=100):
        return self.messages

    def create_session(self, path):
        return 2

    def save_message(self, sid, role, content):
        self.messages.append({"role": role, "content": content})

class MockFacts:
    def get_all(self, path):
        return {}

class MockPins:
    def get_all(self, path):
        return []

def test_slash_metadata_integrity():
    assert len(SLASH_METADATA) >= 20
    cmds = [cmd for cmd, _, _ in SLASH_METADATA]
    assert "/help" in cmds
    assert "/connect" in cmds
    assert "/models" in cmds
    assert "/init" in cmds
    assert "/export" in cmds
    assert "/context" in cmds
    assert "/rename" in cmds
    assert "/editor" in cmds

def test_dispatch_integrity():
    from nexa.commands.ai.slash_commands import SLASH_METADATA, SLASH_DISPATCH, SlashCommandHandler
    ignored = {
        "/help", "/status", "/exit", "/commands", "/q", "/quit", "/new", "/clear",
        "/history", "/load", "/session", "/sessions", "/select-provider", "/set-model",
        "/set-api-key", "/dir", "/explain", "/plan", "/facts", "/pin", "/pins",
        "/unpin", "/clearpins", "/details", "/thinking", "/summarize", "/resume",
        "/continue"
    }
    for cmd, _, _ in SLASH_METADATA:
        if cmd in ignored:
            continue
        assert cmd in SLASH_DISPATCH, f"{cmd} ada di help tapi tidak di dispatch!"
        handler_name, _ = SLASH_DISPATCH[cmd]
        assert hasattr(SlashCommandHandler, handler_name), f"{cmd} -> handler {handler_name} tidak ada!"

def test_slash_handler_execution(tmp_path):
    runtime = MockRuntime()
    mem = MockMemory()
    facts = MockFacts()
    pins = MockPins()
    handler = SlashCommandHandler(runtime, str(tmp_path), mem, facts, pins, "django")

    # /init
    assert handler.handle_init("", "") is True
    assert os.path.exists(tmp_path / "AGENTS.md")
    # /rename
    assert handler.handle_rename("My New Session", "") is True
    assert mem.sessions[1] == "My New Session"
    # /export
    assert handler.handle_export("", "") is True
    assert os.path.exists(tmp_path / "exports")
    # /context
    assert handler.handle_context("", "") is True
    # /agents
    assert handler.handle_agents("", "") is True
    # /timeline, /skills, /variants, /mcps
    assert handler.handle_timeline("", "") is True
    assert handler.handle_skills("", "") is True
    assert handler.handle_variants("", "") is True
    assert handler.handle_mcps("", "") is True
    # /mode
    assert handler.handle_mode("BUILD", "") is True
    assert handler.handle_mode("PLAN", "") is True
    # /undo and /redo
    assert handler.handle_undo("", "") is True
    assert handler.handle_redo("", "") is True

def test_slash_aliases():
    assert SLASH_ALIASES["/q"] == "/exit"
    assert SLASH_ALIASES["/new"] == "/clear"
    assert SLASH_ALIASES["/summarize"] == "/compact"
    assert SLASH_ALIASES["/resume"] == "/sessions"

def test_delete_last_message(tmp_path):
    from nexa.core.ai.memory.core import ChatMemoryManager
    db_path = str(tmp_path / "test_mem.db")
    mem = ChatMemoryManager(db_path=db_path)
    sid = mem.create_session("p")
    mem.save_message(sid, "user", "msg1")
    mem.save_message(sid, "assistant", "msg2")
    
    assert len(mem.load_session_messages(sid)) == 2
    assert mem.delete_last_message(sid) is True
    msgs = mem.load_session_messages(sid)
    assert len(msgs) == 1
    assert msgs[0]["content"] == "msg1"

def test_undo_and_redo_flow(tmp_path):
    from nexa.core.ai.memory.core import ChatMemoryManager
    db_path = str(tmp_path / "test_flow.db")
    mem = ChatMemoryManager(db_path=db_path)
    sid = mem.create_session(str(tmp_path))
    mem.save_message(sid, "user", "original message")
    
    runtime = MockRuntime()
    runtime.session_id = sid
    facts = MockFacts()
    pins = MockPins()
    handler = SlashCommandHandler(runtime, str(tmp_path), mem, facts, pins, "django")
    
    assert len(mem.load_session_messages(sid)) == 1
    # Undo
    assert handler.handle_undo("", "") is True
    assert len(mem.load_session_messages(sid)) == 0
    assert os.path.exists(tmp_path / ".nexa" / "undo_stack.json")
    
    # New instance simulates closing and reopening shell session
    new_handler = SlashCommandHandler(runtime, str(tmp_path), mem, facts, pins, "django")
    assert len(new_handler._redo_stack) == 1

    # Redo on new instance
    assert new_handler.handle_redo("", "") is True
    msgs = mem.load_session_messages(sid)
    assert len(msgs) == 1
    assert msgs[0]["content"] == "original message"

def test_handle_editor(monkeypatch, tmp_path):
    from nexa.core.ai.memory.core import ChatMemoryManager
    db_path = str(tmp_path / "test_ed.db")
    mem = ChatMemoryManager(db_path=db_path)
    sid = mem.create_session(str(tmp_path))
    
    fake_editor = tmp_path / "fake_editor.py"
    fake_editor.write_text(
        "import sys\n"
        "with open(sys.argv[1], 'w', encoding='utf-8') as f:\n"
        "    f.write('Written by CLI editor')\n"
    )
    monkeypatch.setenv("EDITOR", f'"{sys.executable}" "{fake_editor.as_posix()}"')
    
    runtime = MockRuntime()
    runtime.session_id = sid
    facts = MockFacts()
    pins = MockPins()
    handler = SlashCommandHandler(runtime, str(tmp_path), mem, facts, pins, "django")
    
    assert handler.handle_editor("", "") is True
    msgs = mem.load_session_messages(sid)
    assert len(msgs) == 1
    assert "Written by CLI editor" in msgs[0]["content"]

def test_handle_copy(tmp_path):
    from nexa.core.ai.memory.core import ChatMemoryManager
    db_path = str(tmp_path / "test_cp.db")
    mem = ChatMemoryManager(db_path=db_path)
    sid = mem.create_session(str(tmp_path))
    mem.save_message(sid, "assistant", "Sample AI generated response")
    
    runtime = MockRuntime()
    runtime.session_id = sid
    facts = MockFacts()
    pins = MockPins()
    handler = SlashCommandHandler(runtime, str(tmp_path), mem, facts, pins, "django")
    assert handler.handle_copy("", "Sample AI generated response") is True

class MockEventBus:
    def __init__(self, events):
        self._events = events
    def get_history(self, limit=50):
        return self._events[-limit:]

def test_handle_timeline(tmp_path):
    from nexa.core.models.events import EventContext
    from nexa.core.models.enums import EventPriority
    evt = EventContext(
        event_name="TokenUsage",
        timestamp="2026-08-14T00:00:00",
        source="UsageTrackingProvider",
        priority=EventPriority.NORMAL,
        session_id="1",
        payload={"prompt_tokens": 120, "completion_tokens": 60}
    )
    runtime = MockRuntime()
    runtime.bus = MockEventBus([evt])
    handler = SlashCommandHandler(runtime, str(tmp_path), MockMemory(), MockFacts(), MockPins(), "django")
    assert handler.handle_timeline("", "") is True

def test_handle_skills(tmp_path):
    skill_dir = tmp_path / "skills" / "demo_skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Demo Skill\nInstructions here.")
    
    runtime = MockRuntime()
    handler = SlashCommandHandler(runtime, str(tmp_path), MockMemory(), MockFacts(), MockPins(), "django")
    assert handler.handle_skills("", "") is True

def test_handle_variants(tmp_path):
    runtime = MockRuntime()
    handler = SlashCommandHandler(runtime, str(tmp_path), MockMemory(), MockFacts(), MockPins(), "django")
    assert handler.handle_variants("", "") is True

def test_handle_mcps(tmp_path):
    import json
    mcp_file = tmp_path / "mcp_config.json"
    mcp_file.write_text(json.dumps({
        "mcpServers": {
            "fetch": {"command": "npx -y @modelcontextprotocol/server-fetch"}
        }
    }))
    runtime = MockRuntime()
    handler = SlashCommandHandler(runtime, str(tmp_path), MockMemory(), MockFacts(), MockPins(), "django")
    assert handler.handle_mcps("", "") is True

def test_load_agents_instructions(tmp_path):
    assert load_agents_instructions(str(tmp_path)) == ""
    agents = tmp_path / "AGENTS.md"
    agents.write_text("# Rules\nAlways lint before push.", encoding="utf-8")
    assert load_agents_instructions(str(tmp_path)) == "# Rules\nAlways lint before push."
    long_content = "x" * 12000
    agents.write_text(long_content, encoding="utf-8")
    assert len(load_agents_instructions(str(tmp_path))) == 8000


def test_todo_store_and_tools(tmp_path):
    from nexa.core.agent.tools.todo import TodoStore, register_todo_tools
    from nexa.core.agent.tools.registry import ToolRegistry

    store = TodoStore(str(tmp_path))
    assert store.list_todos() == []

    item1 = store.add_todo("Write unit tests")
    assert item1["id"] == 1
    assert item1["status"] == "pending"

    item2 = store.add_todo("Refactor architecture")
    assert item2["id"] == 2

    # Update
    updated = store.update_todo(1, "done")
    assert updated["status"] == "done"

    # Remove
    assert store.remove_todo(2) is True
    assert len(store.list_todos()) == 1

    # Clear
    store.clear_todos()
    assert store.list_todos() == []

    # Test Tools Registration
    registry = ToolRegistry()
    store2 = register_todo_tools(registry, str(tmp_path))
    assert "todo_list" in registry._tools
    assert "todo_add" in registry._tools
    assert "todo_update" in registry._tools

    res_add = registry.execute("todo_add", {"title": "Verify coverage"})
    assert "created" in res_add
    res_list = registry.execute("todo_list", {})
    assert "Verify coverage" in res_list
    res_upd = registry.execute("todo_update", {"id": 1, "status": "done"})
    assert "updated" in res_upd


def test_handle_todos(tmp_path):
    from nexa.core.agent.tools.todo import TodoStore
    runtime = MockRuntime()
    runtime.todo_store = TodoStore(str(tmp_path))
    handler = SlashCommandHandler(runtime, str(tmp_path), MockMemory(), MockFacts(), MockPins(), "django")

    assert handler.handle_todos("", "") is True
    assert handler.handle_todos("add Setup Database", "") is True
    assert len(runtime.todo_store.list_todos()) == 1

    assert handler.handle_todos("done 1", "") is True
    assert runtime.todo_store.list_todos()[0]["status"] == "done"

    assert handler.handle_todos("remove 1", "") is True
    assert len(runtime.todo_store.list_todos()) == 0

