import pytest
from nexa.core.ai.knowledge.orchestrator import KnowledgeOrchestrator, CapabilityResolver
from nexa.core.ai.knowledge.need import Need

def test_capability_resolver_hints():
    user_goal = "Tolong cari file login.html dan ubah warnanya"
    needs = [Need.TEMPLATE_LOOKUP]
    
    hints = CapabilityResolver.build_hints(user_goal, needs)
    
    assert hints["extension"] == ".html"
    assert hints["template_name"] == "login.html"

def test_knowledge_orchestrator_initialization(mocker):
    # Mock registry so it doesn't try to access real git repo on init
    mocker.patch('nexa.core.ai.knowledge.orchestrator.ToolRegistry')
    mocker.patch('nexa.core.agent.tools.knowledge.register_knowledge_tools')
    mocker.patch('nexa.core.ai.knowledge.orchestrator.SQLiteCache')
    mocker.patch('nexa.core.ai.knowledge.cache.sqlite.SQLiteCache')
    
    orchestrator = KnowledgeOrchestrator(workspace_path="/fake/path", tool_budget=5)
    assert orchestrator.tool_budget == 5
    assert orchestrator.workspace_path == "/fake/path"

def test_orchestrator_budget_limit(mocker):
    # If needs require more than tool_budget, it should stop
    mocker.patch('nexa.core.ai.knowledge.orchestrator.ToolRegistry')
    mocker.patch('nexa.core.agent.tools.knowledge.register_knowledge_tools')
    mocker.patch('nexa.core.ai.knowledge.orchestrator.SQLiteCache')
    mocker.patch('nexa.core.ai.knowledge.cache.sqlite.SQLiteCache')
    
    # Tool budget = 0 means it should fail all needs instantly
    orchestrator = KnowledgeOrchestrator(workspace_path="/fake/path", tool_budget=0)
    
    needs = [Need.REPOSITORY_STATUS, Need.PROJECT_STRUCTURE]
    bundle = orchestrator.gather(needs)
    
    # Both needs should be marked as failed because budget is 0
    assert len(bundle.needs_failed) == 2
    assert Need.REPOSITORY_STATUS.value in bundle.needs_failed
    assert bundle.tool_calls_used == 0
