import pytest
from nexa.core.agent.tools.registry import ToolRegistry
from nexa.core.agent.tools.models import ToolMetadata, KnowledgeRequest
from nexa.core.agent.tools.strategies import CheapestFirst, FastestFirst
from nexa.core.agent.tools.prioritizer import ToolPrioritizer
from nexa.core.ai.context.builder import ContextBuilder
from nexa.core.ai.knowledge.intent import IntentEngine
from nexa.core.ai.knowledge.pipeline import KnowledgeAcquisitionPipeline

def dummy_git_status():
    return "M  README.md"

def dummy_git_diff():
    return "+ modified text"

def dummy_write_file():
    return "Wrote file."

@pytest.fixture
def registry():
    reg = ToolRegistry()
    reg.register(
        "git_status", 
        dummy_git_status, 
        {}, 
        metadata=ToolMetadata("git_status", cost=1, latency="fast", category="git", read_only=True, priority=100)
    )
    reg.register(
        "git_diff", 
        dummy_git_diff, 
        {}, 
        metadata=ToolMetadata("git_diff", cost=5, latency="medium", category="git", read_only=True, priority=90)
    )
    reg.register(
        "write_file", 
        dummy_write_file, 
        {}, 
        metadata=ToolMetadata("write_file", cost=10, latency="slow", category="file", read_only=False, priority=10)
    )
    return reg

def test_strategies(registry):
    tools = [
        registry.get_metadata("git_status"),
        registry.get_metadata("git_diff"),
        registry.get_metadata("write_file")
    ]
    
    # CheapestFirst should put git_status first (cost 1)
    cheapest = CheapestFirst()
    sorted_cheap = cheapest.sort_tools(tools)
    assert sorted_cheap[0].name == "git_status"
    assert sorted_cheap[-1].name == "write_file"
    
def test_prioritizer_read_only_enforcement(registry):
    prioritizer = ToolPrioritizer(registry)
    
    # Simulating a request that tries to ask for a file write category
    req = KnowledgeRequest(need="file", intent_domain="general")
    
    # Because 'write_file' is read_only=False, it should NOT be included in the relevant tools.
    # The prioritizer should fallback or raise an error if a Write tool somehow passed the filter.
    # We will test that `resolve_knowledge_request` does not execute write_file.
    
    context = prioritizer.resolve_knowledge_request(req)
    # The output should NOT contain write_file output since it was filtered out.
    assert "Wrote file." not in context

def test_knowledge_pipeline(registry):
    prioritizer = ToolPrioritizer(registry, strategy=CheapestFirst())
    builder = ContextBuilder()
    intent_engine = IntentEngine()
    
    pipeline = KnowledgeAcquisitionPipeline(prioritizer, builder, intent_engine)
    
    # We ask for a commit. The intent engine should map 'commit' (or we explicitly pass need)
    # Since we passed 'git_context', the prioritizer should pick git tools.
    
    final_context = pipeline.acquire_context(user_goal="commit my code", need="git_context")
    
    # The context should include outputs from git_status and git_diff
    assert "SYSTEM CONTEXT" in final_context
    assert "M  README.md" in final_context
    assert "+ modified text" in final_context
    assert "Wrote file." not in final_context # Write tool was correctly skipped
