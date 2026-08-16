import json
import datetime
from typing import List, Dict, Any, Optional, Callable
from nexa.config import Config
from nexa.core.events.bus import PipelineBus, EventContext
from nexa.core.models.enums import EventPriority
from nexa.core.ai.providers.factory import ProviderFactory

class AgentLoop:
    """
    Iterative Autonomous Agent Loop (Phase G / Gap #1).
    Executes multiple turns: LLM -> tool call -> tool result -> LLM, until goal completed or max iterations reached.
    """
    def __init__(
        self,
        runtime,
        system_prompt: str = "",
        max_iterations: Optional[int] = None,
        provider: Optional[Any] = None,
        on_step_callback: Optional[Callable[[int, Dict[str, Any]], None]] = None
    ):
        self.runtime = runtime
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations or Config.get("agent.max_iterations", 12)
        self.provider = provider
        self.on_step_callback = on_step_callback

    def _get_provider(self):
        if self.provider:
            return self.provider
        return ProviderFactory.create()

    def run(self, user_input: str, conversation_history: Optional[List[Dict[str, Any]]] = None) -> str:
        provider = self._get_provider()
        tools_registry = getattr(self.runtime, "tools", None)
        mode = Config.get("agent.mode", "PLAN").upper()

        # Build tools schema according to mode
        tools_schema = []
        if tools_registry:
            if mode == "PLAN":
                # In PLAN mode, only provide read-only tools
                all_schemas = tools_registry.get_all_schemas()
                meta_dict = tools_registry.get_all_metadata()
                for s in all_schemas:
                    tname = s.get("function", {}).get("name", "")
                    meta = meta_dict.get(tname)
                    if meta and meta.read_only:
                        tools_schema.append(s)
            else:
                # In BUILD mode, provide all registered tools
                tools_schema = tools_registry.get_all_schemas()

        messages: List[Dict[str, Any]] = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})

        if conversation_history:
            messages.extend(conversation_history)

        messages.append({"role": "user", "content": user_input})

        bus = getattr(self.runtime, "bus", None)
        session_id = getattr(self.runtime, "session_id", 0)

        for iteration in range(1, self.max_iterations + 1):
            if bus:
                bus.publish_async(EventContext(
                    event_name="AgentLoopIteration",
                    timestamp=datetime.datetime.now().isoformat(),
                    source="AgentLoop",
                    priority=EventPriority.NORMAL,
                    session_id=session_id,
                    payload={"iteration": iteration, "max_iterations": self.max_iterations}
                ))

            try:
                resp = provider.generate(messages, tools=tools_schema if tools_schema else None)
            except Exception as e:
                err_msg = f"Error communicating with AI Provider: {e}"
                if bus:
                    bus.publish_async(EventContext(
                        event_name="ExecutionFailed",
                        timestamp=datetime.datetime.now().isoformat(),
                        source="AgentLoop",
                        priority=EventPriority.HIGH,
                        session_id=session_id,
                        payload={"error": err_msg}
                    ))
                return err_msg

            if not isinstance(resp, dict):
                content = str(resp)
                return content

            tool_calls = resp.get("tool_calls")
            content = resp.get("content", "")

            # Track token usage if available
            usage = resp.get("usage", {})
            if usage and bus:
                bus.publish_async(EventContext(
                    event_name="TokenUsage",
                    timestamp=datetime.datetime.now().isoformat(),
                    source="AgentLoop",
                    priority=EventPriority.LOW,
                    session_id=session_id,
                    payload={
                        "prompt_tokens": usage.get("prompt_tokens", 0) or usage.get("input_tokens", 0) or 0,
                        "completion_tokens": usage.get("completion_tokens", 0) or usage.get("output_tokens", 0) or 0
                    }
                ))

            if tool_calls:
                # Append assistant message with tool calls
                messages.append({
                    "role": "assistant",
                    "content": content or "",
                    "tool_calls": tool_calls
                })

                for call in tool_calls:
                    func_info = call.get("function", {}) if "function" in call else call
                    tool_name = func_info.get("name", "")
                    tool_args = func_info.get("arguments", {})

                    if isinstance(tool_args, str):
                        try:
                            tool_args = json.loads(tool_args)
                        except Exception:
                            tool_args = {}

                    if bus:
                        bus.publish_async(EventContext(
                            event_name="ToolCalled",
                            timestamp=datetime.datetime.now().isoformat(),
                            source="AgentLoop",
                            priority=EventPriority.NORMAL,
                            session_id=session_id,
                            payload={"tool_name": tool_name, "status": "running", "args": tool_args}
                        ))

                    # Execute tool via ToolRegistry
                    if tools_registry:
                        try:
                            tool_result = tools_registry.execute(tool_name, tool_args)
                        except Exception as ex:
                            tool_result = f"Error executing tool {tool_name}: {ex}"
                    else:
                        tool_result = f"Error: Tool registry not available to execute {tool_name}."

                    tool_result_str = str(tool_result) if not isinstance(tool_result, str) else tool_result

                    messages.append({
                        "role": "tool",
                        "tool_call_id": call.get("id", f"call_{iteration}_{tool_name}"),
                        "name": tool_name,
                        "content": tool_result_str
                    })

                    if self.on_step_callback:
                        self.on_step_callback(iteration, {"tool": tool_name, "args": tool_args, "result": tool_result_str})

                # Loop continues to give tool results back to LLM
                continue
            else:
                # LLM provided a final response without any further tool calls
                return content or "(No response content returned)"

        return f"[*] Reached maximum reasoning iterations ({self.max_iterations})."
