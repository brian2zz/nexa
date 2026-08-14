import pytest
import os
import sys
from nexa.commands.ai.slash_commands import SLASH_METADATA, SLASH_ALIASES, SlashCommandHandler
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

def test_slash_handler_execution(tmp_path):
    runtime = MockRuntime()
    mem = MockMemory()
    facts = MockFacts()
    pins = MockPins()
    handler = SlashCommandHandler(runtime, str(tmp_path), mem, facts, pins, "django")

    # /help
    assert handler.handle_help("", "") is True
    # /status
    assert handler.handle_status("", "") is True
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
    
    # Redo
    assert handler.handle_redo("", "") is True
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
