import os
import json
import time
import pytest
import shutil
from nexa.core.agent.indexer import WorkspaceIndexer
from nexa.core.agent.tools.knowledge.file import FileTool

@pytest.fixture
def temp_workspace(tmp_path):
    # Setup chained call sample
    sample_code = """
def fetch_data():
    pass

def process_data():
    fetch_data()
    return True

class RequestHandler:
    def handle_request(self):
        process_data()
        
def main():
    handler = RequestHandler()
    handler.handle_request()
"""
    file_path = tmp_path / "chained.py"
    file_path.write_text(sample_code, encoding="utf-8")
    
    yield str(tmp_path)
    
    # Teardown if necessary
    try:
        # Avoid file locking issues in Windows by letting pytest handle cleanup
        pass
    except Exception:
        pass

def test_call_graph_golden(temp_workspace):
    # 1. Init indexer and scan
    indexer = WorkspaceIndexer(temp_workspace)
    # Perform sync scan for testing
    indexer._do_scan()
    
    # 2. Test query_call_graph directly
    graph = indexer.query_call_graph("process_data")
    assert "handle_request" in graph["callers"], f"Expected handle_request in callers, got {graph['callers']}"
    assert "fetch_data" in graph["callees"], f"Expected fetch_data in callees, got {graph['callees']}"
    
    # 3. Test FileTool read_symbol
    file_tool = FileTool(workspace_path=temp_workspace)
    # Sleep briefly to ensure async scan in FileTool finishes if it overrides our scan, 
    # but actually indexer._do_scan() already indexed it and prevents re-scan.
    
    result = file_tool.read_symbol("process_data")
    assert "not found" not in result.lower(), "Symbol process_data should be found"
    
    data = json.loads(result)
    assert len(data) > 0, "Expected at least one symbol matched"
    
    symbol_info = data[0]
    assert "callers" in symbol_info
    assert "callees" in symbol_info
    assert "handle_request" in symbol_info["callers"]
    assert "fetch_data" in symbol_info["callees"]
