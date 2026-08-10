from nexa.core.agent.tools.registry import ToolRegistry
from nexa.core.agent.tools.models import ToolMetadata
from nexa.core.agent.tools.terminal import TerminalTool
from nexa.core.agent.tools.filesystem import FilesystemTool
from nexa.core.agent.tools.tasks import TaskTool

def register_execution_tools(registry: ToolRegistry, workspace_path: str, bus=None, session_id: int = 0):
    """
    Registers powerful execution tools (bash, write, edit, tasks) to the registry.
    """
    terminal = TerminalTool(workspace_path)
    fs = FilesystemTool(workspace_path)
    tasks = TaskTool(bus, session_id)

    # 1. run_bash_command
    registry.register(
        name="run_bash_command",
        func=terminal.run_bash_command,
        schema={
            "type": "function",
            "function": {
                "name": "run_bash_command",
                "description": "Execute a bash/terminal command in the workspace. Returns stdout and stderr. Use this to run tests, git commands, build scripts, or any standard terminal utility.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The terminal command to execute (e.g. 'npm run test', 'git status', 'ls -la')."
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Optional timeout in seconds. Default is 60."
                        }
                    },
                    "required": ["command"]
                }
            }
        },
        metadata=ToolMetadata(name="run_bash_command", cost=100, latency="high", category="execution", read_only=False, capabilities=["terminal", "execution"], priority=90)
    )

    # 2. list_directory
    registry.register(
        name="list_directory",
        func=fs.list_directory,
        schema={
            "type": "function",
            "function": {
                "name": "list_directory",
                "description": "List files and folders in a specific directory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The directory path to list relative to workspace (e.g. '.', 'src/components')."
                        }
                    },
                    "required": ["path"]
                }
            }
        },
        metadata=ToolMetadata(name="list_directory", cost=5, latency="low", category="filesystem", read_only=True, capabilities=["filesystem", "read"], priority=10)
    )

    # 3. write_file
    registry.register(
        name="write_file",
        func=fs.write_file,
        schema={
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Create a new file or completely overwrite an existing file with new content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "The relative path of the file to write (e.g. 'src/utils.py')."
                        },
                        "content": {
                            "type": "string",
                            "description": "The complete content to write into the file."
                        }
                    },
                    "required": ["filepath", "content"]
                }
            }
        },
        metadata=ToolMetadata(name="write_file", cost=50, latency="medium", category="filesystem", read_only=False, capabilities=["filesystem", "write"], priority=80)
    )

    # 4. edit_file_content
    registry.register(
        name="edit_file_content",
        func=fs.edit_file_content,
        schema={
            "type": "function",
            "function": {
                "name": "edit_file_content",
                "description": "Surgically edit a file by replacing an exact block of code with a new block of code. Much more token-efficient than write_file for small changes in large files.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "The relative path of the file to edit."
                        },
                        "search_block": {
                            "type": "string",
                            "description": "The EXACT string to find in the file. Must include exact whitespace, indentation, and newlines. Must be unique within the file."
                        },
                        "replace_block": {
                            "type": "string",
                            "description": "The new string that will replace the search_block."
                        }
                    },
                    "required": ["filepath", "search_block", "replace_block"]
                }
            }
        },
        metadata=ToolMetadata(name="edit_file_content", cost=50, latency="medium", category="filesystem", read_only=False, capabilities=["filesystem", "edit"], priority=85)
    )

    # 5. manage_tasks
    registry.register(
        name="manage_tasks",
        func=tasks.manage_tasks,
        schema={
            "type": "function",
            "function": {
                "name": "manage_tasks",
                "description": "Manage the agent's internal todo list. The user can see this list in their UI. Use this to track multi-step complex tasks.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["add", "complete", "remove", "list"],
                            "description": "The action to perform."
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the task (required for 'add')."
                        },
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task (required for 'complete' and 'remove')."
                        }
                    },
                    "required": ["action"]
                }
            }
        },
        metadata=ToolMetadata(name="manage_tasks", cost=5, latency="low", category="management", read_only=False, capabilities=["tasks"], priority=50)
    )
