import pytest
from typing import List, Dict, Any
from nexa.core.agent.loop import AgentLoop
from nexa.core.agent.tools.registry import ToolRegistry
from nexa.core.agent.tools.models import ToolMetadata
from nexa.core.events.bus import PipelineBus


class FakeProvider:
    def __init__(self, responses: List[Dict[str, Any]]):
        self.responses = responses
        self.call_count = 0
        self.received_messages = []

    def generate(self, messages: List[Dict[str, Any]], temperature: float = 0.2, tools: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.received_messages.append(messages)
        if self.call_count < len(self.responses):
            resp = self.responses[self.call_count]
            self.call_count += 1
            return resp
        return {"content": "Final fallback"}


class FakeRuntime:
    def __init__(self):
        self.bus = PipelineBus(max_workers=2)
        self.session_id = "test-session"
        self.tools = ToolRegistry()


def test_agent_loop_direct_response():
    provider = FakeProvider([{"content": "Hello world!"}])
    runtime = FakeRuntime()
    loop = AgentLoop(runtime=runtime, system_prompt="System prompt", provider=provider)

    res = loop.run("Hi there")
    assert res == "Hello world!"
    assert provider.call_count == 1


def test_agent_loop_with_tool_call():
    runtime = FakeRuntime()
    # Register a tool
    def mock_search(query: str):
        return f"Results for: {query}"

    runtime.tools.register(
        "mock_search",
        mock_search,
        {
            "type": "function",
            "function": {
                "name": "mock_search",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"]
                }
            }
        },
        ToolMetadata(name="mock_search", cost=1, latency="fast", category="search", read_only=True, priority=100)
    )

    # 1st turn: call tool mock_search. 2nd turn: final answer.
    provider = FakeProvider([
        {
            "content": "Searching...",
            "tool_calls": [
                {
                    "id": "call_1",
                    "function": {"name": "mock_search", "arguments": '{"query": "Django"}'}
                }
            ]
        },
        {
            "content": "Found Django results: Results for: Django"
        }
    ])

    loop = AgentLoop(runtime=runtime, system_prompt="Sys", provider=provider, max_iterations=5)
    res = loop.run("Search for Django")

    assert "Found Django results" in res
    assert provider.call_count == 2
    # Verify tool output was injected to messages in turn 2
    second_turn_msgs = provider.received_messages[1]
    tool_msg = next((m for m in second_turn_msgs if m.get("role") == "tool"), None)
    assert tool_msg is not None
    assert tool_msg["content"] == "Results for: Django"


def test_agent_loop_max_iterations():
    # Provider keeps calling tools indefinitely
    provider = FakeProvider([
        {
            "tool_calls": [{"id": f"call_{i}", "function": {"name": "non_existent", "arguments": "{}"}}]
        }
        for i in range(10)
    ])
    runtime = FakeRuntime()
    loop = AgentLoop(runtime=runtime, provider=provider, max_iterations=3)
    res = loop.run("Infinite loop test")
    assert "Reached maximum reasoning iterations (3)" in res
    assert provider.call_count == 3
