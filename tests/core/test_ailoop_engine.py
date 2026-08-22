import json

import pytest

import nexa.core.ai.agent_loop as agent_loop_mod
from nexa.core.ai.agent_loop import AILoopEngine
from nexa.core.ai.planner.schema import PlannerContext


class FakeProvider:
    def __init__(self, responses, error=None):
        self.responses = responses
        self.error = error
        self.call_count = 0
        self.received_tools = None

    def generate(self, messages, tools=None):
        self.call_count += 1
        self.received_tools = tools
        if self.error:
            raise self.error
        resp = self.responses[self.call_count - 1]
        return resp


def make_context(tmp_path, goal="Add a login feature"):
    return PlannerContext(
        project_path=str(tmp_path),
        knowledge_context="",
        project_facts={},
        pinned_memory=[],
        conversation_memory=[],
        user_goal=goal,
    )


def fake_provider(responses, error=None):
    provider = FakeProvider(responses, error=error)

    def _create():
        return provider

    provider._create = _create
    return provider


@pytest.fixture
def patch_factory(monkeypatch):
    def _patch(provider):
        monkeypatch.setattr(agent_loop_mod.ProviderFactory, "create", provider._create)
    return _patch


FINAL_PLAN = json.dumps({
    "summary": "Plan ready",
    "objective": "Add login",
    "constraints": ["Use existing DB"],
    "work_items": [
        {"title": "Create auth model", "description": "db model", "affected_files": ["app/models.py"], "objective": "auth"}
    ],
    "acceptance_criteria": [
        {"description": "Login works", "priority": "MUST", "verification_method": "manual test"}
    ],
    "risk_analysis": [
        {"category": "Security", "probability": "LOW", "impact": "HIGH", "mitigation": "Review"}
    ],
    "clarifications": [],
})


def test_ailoop_final_plan_success(tmp_path, patch_factory):
    provider = fake_provider([{"content": FINAL_PLAN}])
    patch_factory(provider)

    engine = AILoopEngine()
    report = engine.run_loop(make_context(tmp_path))

    assert report.success is True
    assert len(report.plan.work_items) == 1
    assert report.plan.work_items[0].title == "Create auth model"
    assert report.plan.acceptance_criteria[0].priority == "MUST"


def test_ailoop_builds_system_prompt_with_agents_md(tmp_path):
    (tmp_path / "AGENTS.md").write_text("Always lint before push.", encoding="utf-8")
    engine = AILoopEngine()
    prompt = engine._build_system_prompt(make_context(tmp_path))
    assert "Always lint before push." in prompt
    assert "Nexa AI" in prompt


def test_ailoop_registers_tools_in_plan_mode(tmp_path, patch_factory):
    provider = fake_provider([{"content": FINAL_PLAN}])
    patch_factory(provider)

    engine = AILoopEngine()
    report = engine.run_loop(make_context(tmp_path))

    assert report.success is True
    tool_names = {s.get("function", {}).get("name") for s in provider.received_tools}
    assert "file_read" in tool_names
    assert "content_search" in tool_names
    assert "file_lookup" in tool_names


def test_ailoop_handles_intermediate_remark_and_synthesizes_plan(tmp_path, patch_factory):
    provider = fake_provider([
        {"content": "Saya melihat ada struktur proyek. Mari saya periksa."},
        {"content": FINAL_PLAN}
    ])
    patch_factory(provider)

    engine = AILoopEngine()
    report = engine.run_loop(make_context(tmp_path))

    assert report.success is True
    assert len(report.plan.work_items) == 1
    assert report.plan.work_items[0].title == "Create auth model"


def test_ailoop_llm_error_returns_failed_report(tmp_path, patch_factory):
    provider = fake_provider([], error=RuntimeError("provider down"))
    patch_factory(provider)

    engine = AILoopEngine()
    report = engine.run_loop(make_context(tmp_path))
    assert report.success is False
    assert "LLM Provider Error" in report.error_message
