import os
import sqlite3
import pytest
from nexa.core.agent.indexer import WorkspaceIndexer
from nexa.core.agent.tools.models import KnowledgeRequest, ToolMetadata
from nexa.core.agent.tools.prioritizer import ToolPrioritizer
from nexa.core.agent.tools.registry import ToolRegistry

@pytest.fixture
def temp_workspace(tmp_path):
    workspace = tmp_path / "test_workspace"
    workspace.mkdir()
    
    # Create some dummy files
    (workspace / "test.php").write_text("<?php echo 'hello'; ?>")
    (workspace / "main.py").write_text("print('hello')")
    
    return str(workspace)

def test_workspace_indexer(temp_workspace):
    indexer = WorkspaceIndexer(temp_workspace)
    # Scan synchronously for testing
    indexer.scan_workspace(async_scan=False)
    
    # Query for PHP files
    results = indexer.query_files(extension=".php")
    assert len(results) == 1
    assert "test.php" in results[0]["filename"]
    
    # Query for python files
    results = indexer.query_files(extension=".py")
    assert len(results) == 1
    assert "main.py" in results[0]["filename"]
    
    # Query by name
    results = indexer.query_files(name="test")
    assert len(results) == 1
    assert "test.php" in results[0]["filename"]


def test_tool_prioritizer_capability_routing():
    registry = ToolRegistry()
    registry.register(
        "file_lookup",
        lambda ext, name: "mock",
        schema={"type": "function", "function": {"name": "file_lookup"}},
        metadata=ToolMetadata(name="file_lookup", cost=1, latency="fast", category="file", read_only=True, priority=100, capabilities=["file_lookup", "find_file"])
    )
    registry.register(
        "content_search",
        lambda query, path: "mock",
        schema={"type": "function", "function": {"name": "content_search"}},
        metadata=ToolMetadata(name="content_search", cost=10, latency="slow", category="search", read_only=True, priority=80, capabilities=["content_search", "search_code"])
    )
    
    prioritizer = ToolPrioritizer(registry)
    
    # Requesting file lookup capability
    req = KnowledgeRequest(need="find_file")
    tools = prioritizer.prioritize(req)
    assert len(tools) == 1
    assert tools[0]["function"]["name"] == "file_lookup"
    
    # Requesting content search capability
    req = KnowledgeRequest(need="content_search")
    tools = prioritizer.prioritize(req)
    assert len(tools) == 1
    assert tools[0]["function"]["name"] == "content_search"
