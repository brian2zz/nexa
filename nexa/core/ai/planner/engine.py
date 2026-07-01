import time
import datetime
from typing import Dict, Any, Optional
from nexa.core.ai.providers.factory import ProviderFactory
from nexa.core.events.bus import PipelineBus
from nexa.core.models.events import EventContext
from nexa.core.models.enums import EventPriority
from .schema import PlannerContext
from .validator import PlanValidator
from .report import PlannerReport

class AIPlannerEngine:
    """
    The orchestrator that generates Execution Plans based on deep context.
    """
    def __init__(self, bus: Optional[PipelineBus] = None):
        self.validator = PlanValidator()
        self.bus = bus

    def build_system_prompt(self, context: PlannerContext) -> str:
        prompt = (
            "You are Nexa AI Planner, an elite Software Engineering Architect.\n"
            "Your ONLY responsibility is to create an ExecutionPlan in STRICT JSON format.\n"
            "You DO NOT write code directly, you DO NOT execute commands. You only output a blueprint JSON.\n\n"
        )
        
        prompt += f"Project Path: {context.project_path}\n"
        
        if context.project_facts:
            prompt += "\nProject Facts:\n"
            for k, v in context.project_facts.items():
                prompt += f"- {k}: {v}\n"
                
        if context.pinned_memory:
            prompt += "\nPinned User Preferences (STRICT RULES):\n"
            for p in context.pinned_memory:
                prompt += f"- {p['content']}\n"
                
        if context.knowledge_context:
            prompt += f"\nKnowledge/File Context:\n{context.knowledge_context}\n"
            
        prompt += (
            "\nEXPECTED OUTPUT FORMAT (JSON ONLY):\n"
            "You MUST return a JSON object with at least the 'goal' and 'summary' fields.\n"
            "{\n"
            "  \"goal\": \"string (Describe what you were asked to do)\",\n"
            "  \"summary\": \"string (Provide your detailed final answer, search results, or findings here)\",\n"
            "  \"complexity\": \"low|medium|high\",\n"
            "  \"estimated_time\": \"string\",\n"
            "  \"risk\": \"string\",\n"
            "  \"affected_modules\": [\"string\"],\n"
            "  \"affected_files\": [\"string\"],\n"
            "  \"files_to_create\": [\"string\"],\n"
            "  \"files_to_modify\": [\"string\"],\n"
            "  \"dependencies\": [\"string\"],\n"
            "  \"stages\": [\n"
            "    {\n"
            "      \"name\": \"string (e.g. Preparation, Execution, Verification)\",\n"
            "      \"intents\": [\n"
            "        {\"action\": \"string (e.g. git_commit, terminal_command)\", \"parameters\": {}, \"description\": \"string\"}\n"
            "      ]\n"
            "    }\n"
            "  ],\n"
            "  \"verification_steps\": [\"string\"],\n"
            "  \"warnings\": [\"string\"],\n"
            "  \"recommendations\": [\"string\"],\n"
            "  \"rollback_strategy\": \"string\",\n"
            "  \"confidence\": 1-100\n"
            "}\n\n"
            "CRITICAL RULES FOR TOOLS:\n"
            "1. DO NOT invent or call any tools that are not explicitly provided in the tool schemas.\n"
            "2. NEVER answer questions about the codebase from your internal knowledge. You MUST use the provided function tools ('file_lookup', 'content_search', or 'file_read') to investigate the local project BEFORE providing the final JSON answer.\n"
            "3. If the user asks if a file exists (e.g. 'apakah ada file php'), you MUST call the 'file_lookup' function tool with the 'extension' parameter. Do NOT put 'file_lookup' in your intents.\n"
            "4. If the user asks where a function/class is located, call the 'content_search' function tool. Put the results in the 'summary' and leave 'stages' EMPTY ([]).\n"
            "5. If you need to execute a terminal command, include it as an intent with action='terminal_command' and parameters={\"command\": \"command_string\"}. IMPORTANT: Do NOT use shell redirect operators like >, >>, or | in terminal commands (e.g. do not use 'echo text >> file'). They are blocked. Use action='CREATE' or 'MODIFY' to write files.\n"
            "6. When providing search results in the 'summary', format them beautifully like an advanced AI assistant: specify the exact File Path, Line Number, and include the actual Code Snippet using Markdown code blocks.\n"
            "7. If you search for something and cannot find it, DO NOT hallucinate file names or locations. Explicitly state in the 'summary' that it is not found, and DO NOT add any intents to create it unless requested.\n"
            "8. CRITICAL: You must ACTUALLY CALL the tools (via JSON function calling) to gather data. Do NOT just output a JSON plan saying you will use a tool. Once you have the data, immediately return the final JSON plan.\n"
            "9. NEVER put internal tool names (like 'file_lookup', 'file_read', 'content_search') inside the 'intents' array. Intents are strictly for actual actions. If no actions are needed, leave 'stages' EMPTY ([]).\n"
            "\nCRITICAL INSTRUCTION: Return ONLY the raw JSON object. Do not wrap it in markdown code blocks if possible, or if you do, ensure it is ONLY valid JSON. Escape all newlines in strings as \\n."
        )
        return prompt

    def plan(self, context: PlannerContext, session_id: str = "default_session") -> PlannerReport:
        start_time = time.time()
        timestamp = datetime.datetime.now().isoformat()
        
        if self.bus:
            self.bus.publish(EventContext(
                event_name="BeforePlanning",
                timestamp=timestamp,
                source="PlannerEngine",
                priority=EventPriority.NORMAL,
                session_id=session_id,
                payload={"goal": context.user_goal}
            ))
            
        try:
            provider = ProviderFactory.create()
        except Exception as e:
            error_msg = f"Provider Error: {e}"
            if self.bus:
                self.bus.publish(EventContext(
                    event_name="PlanningFailed",
                    timestamp=datetime.datetime.now().isoformat(),
                    source="PlannerEngine",
                    priority=EventPriority.HIGH,
                    session_id=session_id,
                    duration=time.time() - start_time,
                    payload={"error": error_msg}
                ))
            return PlannerReport(success=False, error_message=error_msg)

        sys_prompt = self.build_system_prompt(context)
        
        # Build chat memory context
        messages = [{"role": "system", "content": sys_prompt}]
        for msg in context.conversation_memory:
            messages.append(msg)
            
        messages.append({"role": "user", "content": f"Create an ExecutionPlan for this goal: {context.user_goal}"})
        
        from nexa.core.agent.tools.registry import ToolRegistry
        from nexa.core.agent.tools.knowledge import register_knowledge_tools
        import json
        
        tool_registry = ToolRegistry()
        register_knowledge_tools(tool_registry, context.project_path)
        tool_schemas = tool_registry.get_all_schemas()
        
        max_iterations = 15
        content = ""
        for _ in range(max_iterations):
            try:
                raw_resp = provider.generate(messages, tools=tool_schemas)
                
                # Check if raw_resp is a dictionary or string
                if isinstance(raw_resp, dict):
                    tool_calls = raw_resp.get("tool_calls", [])
                    content = raw_resp.get("content", "")
                else:
                    tool_calls = []
                    content = str(raw_resp)
                
                if not tool_calls:
                    break
                    
                # Print indicator that tool is being called
                print(f"       [Planner Tool Call]: {tool_calls[0].get('function', {}).get('name')}")
                
                # We have tool calls!
                messages.append({
                    "role": "assistant",
                    "content": content,
                    "tool_calls": tool_calls
                })
                
                break_outer = False
                for tc in tool_calls:
                    func_name = tc.get("function", {}).get("name")
                    args_str = tc.get("function", {}).get("arguments", "{}")
                    try:
                        # DEBUG LOGGING
                        with open("planner_debug.log", "a", encoding="utf-8") as dbg:
                            dbg.write(f"\n[TOOL CALL] {func_name}\nARGS: {args_str}\n")
                            
                        args = json.loads(args_str) if isinstance(args_str, str) else args_str
                        if func_name == "submit_execution_plan":
                            content = args.get("plan_json", "")
                            break_outer = True
                            break
                        # ToolRegistry.execute takes (name, kwargs) as positional arguments
                        result = tool_registry.execute(func_name, args)
                        
                        # DEBUG LOGGING
                        with open("planner_debug.log", "a", encoding="utf-8") as dbg:
                            dbg.write(f"RESULT: {str(result)[:500]}\n")
                            
                    except Exception as e:
                        result = f"Error executing {func_name}: {e}"
                        with open("planner_debug.log", "a", encoding="utf-8") as dbg:
                            dbg.write(f"ERROR: {result}\n")
                        
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.get("id"),
                        "name": func_name,
                        "content": str(result)
                    })
                    
                if break_outer:
                    break
            except Exception as e:
                error_msg = f"Generation Error: {e}"
                if self.bus:
                    self.bus.publish(EventContext(
                        event_name="PlanningFailed",
                        timestamp=datetime.datetime.now().isoformat(),
                        source="PlannerEngine",
                        priority=EventPriority.HIGH,
                        session_id=session_id,
                        duration=time.time() - start_time,
                        payload={"error": error_msg}
                    ))
                return PlannerReport(success=False, error_message=error_msg)
        else:
            # We reached max iterations. Force the LLM to summarize what it found.
            messages.append({"role": "user", "content": "SYSTEM: Max iterations reached. You MUST output your final ExecutionPlan JSON now based on the information you have gathered so far."})
            try:
                raw_resp = provider.generate(messages, tools=[])
                if isinstance(raw_resp, dict):
                    content = raw_resp.get("content", "")
                else:
                    content = str(raw_resp)
            except Exception as e:
                content = f"{{ \"goal\": \"{context.user_goal}\", \"summary\": \"Max iterations reached. Could not generate plan: {e}\", \"stages\": [] }}"
            
        success, error, plan = self.validator.validate(content)
        
        duration = time.time() - start_time
        
        if not success:
            if self.bus:
                self.bus.publish(EventContext(
                    event_name="PlanningFailed",
                    timestamp=datetime.datetime.now().isoformat(),
                    source="PlannerEngine",
                    priority=EventPriority.HIGH,
                    session_id=session_id,
                    duration=duration,
                    payload={"error": error}
                ))
            return PlannerReport(success=False, error_message=error)
            
        if self.bus:
            self.bus.publish(EventContext(
                event_name="AfterPlanning",
                timestamp=datetime.datetime.now().isoformat(),
                source="PlannerEngine",
                priority=EventPriority.NORMAL,
                session_id=session_id,
                duration=duration,
                payload={"goal": context.user_goal, "status": "success"}
            ))
            
        return PlannerReport(success=True, error_message="", plan=plan)
