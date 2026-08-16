import os
import json
from typing import Dict, List, Optional, Any
from .client import MCPClient
from nexa.core.agent.tools.registry import ToolRegistry
from nexa.core.agent.tools.models import ToolMetadata

class MCPManager:
    """
    Manages MCP configuration discovery, lifecycle, and ToolRegistry bridging.
    """

    def __init__(self, cwd: str):
        self.cwd = cwd
        self.config_path = os.path.join(self.cwd, "mcp_config.json")
        self.clients: Dict[str, MCPClient] = {}

    def load_and_register(self, tool_registry: ToolRegistry) -> int:
        """
        Reads mcp_config.json, initializes servers, and registers their tools into tool_registry.
        Returns total number of MCP tools registered.
        """
        if not os.path.exists(self.config_path):
            return 0

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[!] Failed to parse mcp_config.json: {e}")
            return 0

        servers = data.get("mcpServers", {})
        total_tools = 0

        for name, config in servers.items():
            cmd = config.get("command")
            if not cmd:
                continue
            args = config.get("args", [])
            env = config.get("env", None)

            client = MCPClient(server_name=name, command=cmd, args=args, env=env, cwd=self.cwd)
            if client.initialize():
                self.clients[name] = client
                for t in client.tools:
                    tool_name = t.get("name", "unknown")
                    reg_name = f"mcp_{name}_{tool_name}"
                    desc = f"[MCP: {name}] {t.get('description', '')}"
                    input_schema = t.get("inputSchema", {})

                    schema = {
                        "name": reg_name,
                        "description": desc,
                        "parameters": input_schema
                    }

                    # Wrap execution call
                    def make_func(c=client, tn=tool_name):
                        return lambda **kwargs: c.call_tool(tn, kwargs)

                    tool_registry.register(
                        name=reg_name,
                        func=make_func(),
                        schema=schema,
                        metadata=ToolMetadata(
                            name=reg_name,
                            cost=15,
                            latency="medium",
                            category="mcp",
                            read_only=False,
                            priority=40,
                            capabilities=["mcp", name, tool_name]
                        )
                    )
                    total_tools += 1
            else:
                client.stop()

        return total_tools

    def get_status(self) -> Dict[str, Any]:
        """
        Returns status summary of all configured & active MCP servers.
        """
        config_exists = os.path.exists(self.config_path)
        configured_servers = {}
        if config_exists:
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    configured_servers = data.get("mcpServers", {})
            except Exception:
                pass

        return {
            "config_path": self.config_path,
            "config_exists": config_exists,
            "configured_count": len(configured_servers),
            "configured_servers": configured_servers,
            "active_clients": {
                name: {
                    "tools_count": len(client.tools),
                    "tools": [t.get("name") for t in client.tools]
                }
                for name, client in self.clients.items()
            }
        }

    def shutdown_all(self):
        """
        Stops all running MCP client processes.
        """
        for client in self.clients.values():
            client.stop()
        self.clients.clear()
