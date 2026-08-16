import os
import sys

import pytest

from nexa.core.agent.tools.registry import ToolRegistry
from nexa.core.agent.tools.execution_tools import register_execution_tools


@pytest.fixture
def registry(tmp_path):
    reg = ToolRegistry()
    register_execution_tools(reg, str(tmp_path))
    return reg


def test_execution_tools_registered(registry):
    names = registry.get_all_metadata().keys()
    assert {"run_bash_command", "write_file", "edit_file_content", "list_directory", "manage_tasks"} <= set(names)

    # read_only flags
    assert registry.get_metadata("write_file").read_only is False
    assert registry.get_metadata("run_bash_command").read_only is False
    assert registry.get_metadata("edit_file_content").read_only is False
    assert registry.get_metadata("manage_tasks").read_only is False
    assert registry.get_metadata("list_directory").read_only is True


def test_write_edit_list_directory(registry, tmp_path):
    res = registry.execute("write_file", {"filepath": "src/utils.py", "content": "def add(a, b):\n    return a + b\n"})
    assert "Successfully wrote" in res
    assert (tmp_path / "src" / "utils.py").exists()

    res_edit = registry.execute("edit_file_content", {
        "filepath": "src/utils.py",
        "search_block": "    return a + b\n",
        "replace_block": "    return a * b\n",
    })
    assert "Successfully replaced content" in res_edit
    content = (tmp_path / "src" / "utils.py").read_text(encoding="utf-8")
    assert "return a * b" in content

    res_list = registry.execute("list_directory", {"path": "src"})
    assert "utils.py" in res_list


def test_edit_file_not_found(registry):
    res = registry.execute("edit_file_content", {
        "filepath": "missing.py",
        "search_block": "x",
        "replace_block": "y",
    })
    assert "does not exist" in res


def test_path_traversal_blocked(registry, tmp_path):
    res = registry.execute("write_file", {"filepath": "../escape.py", "content": "evil"})
    assert "outside the workspace" in res
    assert not (tmp_path.parent / "escape.py").exists()


def test_run_bash_command(registry, tmp_path):
    cmd = f'"{sys.executable}" -c "print(\'bash-tool-ok\')"'
    res = registry.execute("run_bash_command", {"command": cmd})
    assert "bash-tool-ok" in res
    assert "Code: 0" in res


def test_run_bash_command_error(registry):
    cmd = f'"{sys.executable}" -c "import sys; sys.exit(3)"'
    res = registry.execute("run_bash_command", {"command": cmd})
    assert "Code: 3" in res


def test_manage_tasks(registry):
    res_add = registry.execute("manage_tasks", {"action": "add", "title": "Build feature X"})
    assert "Task added with ID 1" in res_add

    res_list = registry.execute("manage_tasks", {"action": "list"})
    assert "Build feature X" in res_list

    res_complete = registry.execute("manage_tasks", {"action": "complete", "task_id": 1})
    assert "marked as done" in res_complete

    res_remove = registry.execute("manage_tasks", {"action": "remove", "task_id": 1})
    assert "removed" in res_remove

    res_bad = registry.execute("manage_tasks", {"action": "bogus"})
    assert "unknown action" in res_bad
