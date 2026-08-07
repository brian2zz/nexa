import os
import subprocess
import pytest
from nexa.core.ai.knowledge.orchestrator import KnowledgeOrchestrator
from nexa.core.ai.knowledge.need import Need

@pytest.fixture
def real_workspace(tmp_path):
    # Setup temp workspace
    workspace = tmp_path / "test_workspace"
    workspace.mkdir()
    
    # Create a template file
    (workspace / "login.html").write_text("<html><body>Login</body></html>", encoding="utf-8")
    
    # Init git repo
    subprocess.run(["git", "init"], cwd=workspace, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=workspace, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=workspace, capture_output=True)
    
    # Initial commit
    subprocess.run(["git", "add", "."], cwd=workspace, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=workspace, capture_output=True)
    
    # Modify a file to create some status
    (workspace / "login.html").write_text("<html><body>Login Updated</body></html>", encoding="utf-8")
    
    return str(workspace)

def test_knowledge_orchestrator_integration_real(real_workspace):
    orchestrator = KnowledgeOrchestrator(workspace_path=real_workspace, tool_budget=10)
    
    needs = [
        Need.TEMPLATE_LOOKUP,
        Need.FILE_CONTENT,
        Need.PROJECT_STRUCTURE,
        Need.REPOSITORY_STATUS,
        Need.CURRENT_BRANCH,
        Need.GIT_HISTORY
    ]
    
    # Using hints to help deterministic resolution
    hints = {
        "template_name": "login.html",
        "file_path": "login.html"
    }
    
    bundle = orchestrator.gather(needs, context_hints=hints)
    
    # Assert successful tools
    assert Need.TEMPLATE_LOOKUP.value in bundle.needs_satisfied
    assert Need.FILE_CONTENT.value in bundle.needs_satisfied
    assert Need.PROJECT_STRUCTURE.value in bundle.needs_satisfied
    assert Need.REPOSITORY_STATUS.value in bundle.needs_satisfied
    # Note: CURRENT_BRANCH is deduplicated by REPOSITORY_STATUS, so it doesn't appear in needs_satisfied
    assert Need.GIT_HISTORY.value in bundle.needs_satisfied
    
    # Make sure nothing failed (all 6 should pass)
    assert len(bundle.needs_failed) == 0
    
    # Verify the contents of EvidenceBundle
    assert len(bundle.files) > 0
    assert bundle.git.status != ""
    assert "Initial commit" in bundle.git.recent_commits
    
    # The branch might be master or main depending on git config, but it shouldn't be empty
    assert bundle.git.current_branch != ""
