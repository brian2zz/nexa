from nexa.core.agent.tools.knowledge.file import FileTool
from nexa.core.agent.tools.knowledge.search import SearchTool
from nexa.core.agent.tools.models import ToolMetadata

def register_knowledge_tools(registry, cwd: str):
    file_tool = FileTool(workspace_path=cwd)
    search_tool = SearchTool(workspace_path=cwd)
    
    # We expose the domain capabilities to the Planner (KnowledgeRequest)
    # The actual execution happens via these schemas
    
    registry.register(
        "file_lookup",
        file_tool.find,
        schema={
            "type": "function",
            "function": {
                "name": "file_lookup",
                "description": "Find files by extension or name quickly.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "extension": {"type": "string", "description": "The file extension to search for, e.g., '.php'"},
                        "name": {"type": "string", "description": "The file name to search for"}
                    },
                    "required": ["extension"]
                }
            }
        },
        metadata=ToolMetadata(name="file_lookup", cost=1, latency="fast", category="file", read_only=True, priority=100, capabilities=["file_lookup", "find_file", "search_file"])
    )

    registry.register(
        "file_read",
        file_tool.read,
        schema={
            "type": "function",
            "function": {
                "name": "file_read",
                "description": "Read contents of a specific file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string"}
                    },
                    "required": ["filepath"]
                }
            }
        },
        metadata=ToolMetadata(name="file_read", cost=5, latency="medium", category="file", read_only=True, priority=90, capabilities=["read_file", "view_file"])
    )

    registry.register(
        "content_search",
        search_tool.text,
        schema={
            "type": "function",
            "function": {
                "name": "content_search",
                "description": "Search for text content inside files.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "path": {"type": "string"}
                    },
                    "required": ["query"]
                }
            }
        },
        metadata=ToolMetadata(name="content_search", cost=10, latency="slow", category="search", read_only=True, priority=80, capabilities=["content_search", "search_code"])
    )

    # Register Git tools if cwd is provided
    if cwd:
        from .git import register_git_tools
        register_git_tools(registry, cwd)
