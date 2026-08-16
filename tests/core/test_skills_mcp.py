import os
import json
import pytest
from nexa.core.ai.skills import SkillManager, SkillItem
from nexa.core.ai.mcp import MCPManager, MCPClient
from nexa.core.agent.tools.registry import ToolRegistry

def test_skills_manager_parsing_and_injection(tmp_path):
    # Setup mock project skills directory
    skills_dir = tmp_path / "skills" / "django-expert"
    skills_dir.mkdir(parents=True)
    
    skill_file = skills_dir / "SKILL.md"
    skill_file.write_text("""---
name: django-expert
description: Expert guidelines for Django 5.x apps
---
# Django Guidelines
Always use class-based views and proper type annotations.
""", encoding="utf-8")

    mgr = SkillManager(cwd=str(tmp_path))
    skills = mgr.load_all_skills()

    assert len(skills) >= 1
    target = next((s for s in skills if s.name == "django-expert"), None)
    assert target is not None
    assert target.scope == "project"
    assert "Django 5.x apps" in target.description
    assert "class-based views" in target.content

    prompt = mgr.format_skills_for_prompt(skills)
    assert "## Available Autonomous Skills" in prompt
    assert "django-expert" in prompt

def test_mcp_manager_discovery_and_registration(tmp_path):
    mcp_config = tmp_path / "mcp_config.json"
    mcp_config.write_text(json.dumps({
        "mcpServers": {
            "test_server": {
                "command": "python",
                "args": ["-c", "import sys; print('ready')"]
            }
        }
    }), encoding="utf-8")

    mgr = MCPManager(cwd=str(tmp_path))
    status = mgr.get_status()
    assert status["config_exists"] is True
    assert status["configured_count"] == 1
    assert "test_server" in status["configured_servers"]

    tools = ToolRegistry()
    # If server doesn't respond to MCP protocol, it won't register tools but handles gracefully
    count = mgr.load_and_register(tools)
    assert isinstance(count, int)
    mgr.shutdown_all()
