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
            "{\n"
            "  \"goal\": \"string\",\n"
            "  \"summary\": \"string\",\n"
            "  \"complexity\": \"low|medium|high\",\n"
            "  \"estimated_time\": \"string\",\n"
            "  \"risk\": \"string\",\n"
            "  \"affected_modules\": [\"string\"],\n"
            "  \"affected_files\": [\"string\"],\n"
            "  \"files_to_create\": [\"string\"],\n"
            "  \"files_to_modify\": [\"string\"],\n"
            "  \"dependencies\": [\"string\"],\n"
            "  \"execution_steps\": [\n"
            "    {\"action\": \"create|modify|delete|command\", \"target\": \"file/module/command\", \"description\": \"string\"}\n"
            "  ],\n"
            "  \"verification_steps\": [\"string\"],\n"
            "  \"warnings\": [\"string\"],\n"
            "  \"recommendations\": [\"string\"],\n"
            "  \"rollback_strategy\": \"string\",\n"
            "  \"confidence\": 1-100\n"
            "}\n\n"
            "CRITICAL RULES FOR TOOLS:\n"
            "1. DO NOT invent or call any tools that are not explicitly provided in the tool schemas.\n"
            "2. If you need to execute a terminal command (e.g., 'git push', 'git pull', 'npm install'), DO NOT try to call a tool for it. Instead, include it as an execution_step with action='command' and target='command_string' in your final JSON plan.\n"
            "3. If you have gathered enough information, immediately return the JSON.\n"
            "\nCRITICAL INSTRUCTION: Return ONLY the raw JSON object. Do not wrap it in markdown code blocks if possible, or if you do, ensure it is ONLY valid JSON."
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
        
        max_iterations = 5
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
                        args = json.loads(args_str)
                        if func_name == "submit_execution_plan":
                            content = args.get("plan_json", "")
                            break_outer = True
                            break
                        result = tool_registry.execute(func_name, **args)
                    except Exception as e:
                        result = f"Error executing {func_name}: {e}"
                        
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
            if not content:
                content = "{ \"error\": \"Max iterations reached\" }"
            
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
