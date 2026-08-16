import json
import subprocess
import threading
from typing import Dict, Any, Optional, List

class MCPClient:
    """
    Client for Model Context Protocol (MCP) servers communicating over stdio JSON-RPC 2.0.
    """

    def __init__(self, server_name: str, command: str, args: Optional[List[str]] = None, env: Optional[Dict[str, str]] = None, cwd: Optional[str] = None):
        self.server_name = server_name
        self.command = command
        self.args = args or []
        self.env = env
        self.cwd = cwd
        self.process: Optional[subprocess.Popen] = None
        self._request_id = 0
        self._lock = threading.Lock()
        self.tools: List[Dict[str, Any]] = []

    def start(self) -> bool:
        """
        Spawns the MCP server subprocess.
        """
        full_cmd = [self.command] + self.args
        try:
            self.process = subprocess.Popen(
                full_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.cwd,
                env=self.env,
                bufsize=1
            )
            return True
        except Exception as e:
            print(f"[!] Failed to start MCP server '{self.server_name}': {e}")
            return False

    def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Sends a JSON-RPC request to the MCP server and reads the response line.
        """
        if not self.process or self.process.poll() is not None:
            return None

        with self._lock:
            self._request_id += 1
            payload = {
                "jsonrpc": "2.0",
                "id": self._request_id,
                "method": method,
                "params": params or {}
            }
            try:
                msg = json.dumps(payload) + "\n"
                self.process.stdin.write(msg)
                self.process.stdin.flush()

                # Read line from stdout
                line = self.process.stdout.readline()
                if not line:
                    return None
                return json.loads(line)
            except Exception as e:
                return {"error": {"message": str(e)}}

    def initialize(self) -> bool:
        """
        Performs standard MCP handshake: 'initialize' -> 'notifications/initialized' -> 'tools/list'.
        """
        if not self.process:
            if not self.start():
                return False

        init_resp = self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "nexa-ai-agent",
                "version": "1.0.0"
            }
        })

        if not init_resp or "error" in init_resp:
            return False

        # Send initialized notification
        try:
            notif = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}) + "\n"
            self.process.stdin.write(notif)
            self.process.stdin.flush()
        except Exception:
            pass

        # Fetch available tools
        list_resp = self.send_request("tools/list")
        if list_resp and "result" in list_resp:
            self.tools = list_resp["result"].get("tools", [])

        return True

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """
        Calls a tool on the MCP server.
        """
        resp = self.send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })
        if not resp:
            return {"error": "No response from MCP server"}
        if "error" in resp:
            return {"error": resp["error"]}
        return resp.get("result", {})

    def stop(self):
        """
        Gracefully terminates the MCP server process.
        """
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            self.process = None
