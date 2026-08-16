import json
import time
import datetime
import threading
from typing import Dict, Any, Optional

from nexa.core.ai.providers.factory import ProviderFactory
from nexa.core.events.bus import PipelineBus, EventContext
from nexa.core.models.enums import EventPriority
from nexa.core.agent.tools.registry import ToolRegistry
from nexa.core.ai.planner.schema import PlannerContext, PlanningResult, ConfidenceAssessment
from nexa.core.ai.planner.report import PlannerReport
from nexa.core.ai.planner.validator import PlanValidator

class AILoopEngine:
    """
    Phase 1: Iterative Autonomous Agent Loop
    Replaces the rigid linear AIPlannerEngine.
    """
    def __init__(self, bus: Optional[PipelineBus] = None):
        self.bus = bus
        self.provider = ProviderFactory.create()
        self.validator = PlanValidator()

    def _build_system_prompt(self, context: PlannerContext) -> str:
        prompt = (
            "You are Nexa AI, an autonomous software engineering agent. You act as the nexa ai planner (planning engine).\n"
            "You operate in an iterative loop. You can call tools to explore the workspace, read files, and eventually achieve the user's goal.\n"
            "When you have gathered enough information and are ready to propose the final execution plan, you must return a final response.\n"
        )
        prompt += f"\nProject Path: {context.project_path}\n"
        
        # Read AGENTS.md if it exists
        import os
        agents_md_path = os.path.join(context.project_path, "AGENTS.md")
        if os.path.exists(agents_md_path):
            try:
                with open(agents_md_path, 'r', encoding='utf-8') as f:
                    agents_content = f.read()
                prompt += f"\nProject Instructions (AGENTS.md):\n{agents_content}\n"
            except Exception as e:
                prompt += f"\nProject Instructions (AGENTS.md): Found but could not read ({e})\n"
        
        # Autonomous Skills Auto-Injection
        try:
            from nexa.core.ai.skills import SkillManager
            skill_mgr = SkillManager(context.project_path)
            skills_prompt = skill_mgr.format_skills_for_prompt()
            if skills_prompt:
                prompt += f"\n{skills_prompt}\n"
        except Exception:
            pass
        
        if context.project_facts:
            prompt += "\nProject Facts:\n"
            for k, v in context.project_facts.items():
                prompt += f"- {k}: {v}\n"
                
        if context.pinned_memory:
            prompt += "\nPinned Rules:\n"
            for p in context.pinned_memory:
                prompt += f"- {p['content']}\n"
                
        if context.knowledge_context:
            prompt += f"\nAdditional Context:\n{context.knowledge_context}\n"
            
        prompt += (
            "\nCRITICAL RULES:\n"
            "1. ALWAYS call tools to verify file paths and read contents before proposing code changes.\n"
            "2. If you want to use a tool, output a tool call. The system will execute it and return the result to you in the next turn.\n"
            "3. If you have finished gathering knowledge and want to propose the final execution plan, output a raw JSON object matching the PlanningResult schema in your content message (with work_items, acceptance_criteria, risk_analysis). Do NOT call any tools when you output the final JSON plan.\n"
            "4. NEVER output markdown code blocks around the final JSON plan if possible.\n"
            "\nJSON SCHEMA FOR FINAL PLAN:\n"
            "{\n"
            "  \"objective\": \"string\",\n"
            "  \"constraints\": [\"string\"],\n"
            "  \"work_items\": [\n"
            "    {\"title\": \"string\", \"description\": \"string\", \"affected_files\": [\"string\"], \"objective\": \"string\"}\n"
            "  ],\n"
            "  \"acceptance_criteria\": [\n"
            "    {\"description\": \"string\", \"priority\": \"MUST\", \"verification_method\": \"string\"}\n"
            "  ],\n"
            "  \"risk_analysis\": [\n"
            "    {\"category\": \"General\", \"probability\": \"MEDIUM\", \"impact\": \"MEDIUM\", \"mitigation\": \"string\"}\n"
            "  ],\n"
            "  \"clarifications\": []\n"
            "}\n"
        )
        return prompt

    def run_loop(self, context: PlannerContext, session_id: int = 0, max_iterations: int = 15) -> PlannerReport:
        start_time = time.time()
        
        sys_prompt = self._build_system_prompt(context)
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": context.user_goal}
        ]
        
        # Load available knowledge and execution tools
        from nexa.core.agent.tools.knowledge import register_knowledge_tools
        from nexa.core.agent.tools.execution_tools import register_execution_tools
        registry = ToolRegistry()
        register_knowledge_tools(registry, context.project_path)
        register_execution_tools(registry, context.project_path, bus=self.bus, session_id=session_id)
        tool_schemas = registry.get_all_schemas()
        
        iteration = 0
        final_json_content = None
        
        while iteration < max_iterations:
            iteration += 1
            if self.bus:
                self.bus.publish(EventContext(
                    event_name="AgentLoopIteration",
                    timestamp=datetime.datetime.now().isoformat(),
                    source="AILoopEngine",
                    priority=EventPriority.NORMAL,
                    session_id=session_id,
                    payload={"iteration": iteration, "max_iterations": max_iterations}
                ))

            try:
                resp = self.provider.generate(messages, tools=tool_schemas)
            except Exception as e:
                return PlannerReport(success=False, error_message=f"LLM Provider Error: {str(e)}")
            
            content = resp.get("content", "")
            tool_calls = resp.get("tool_calls", [])
            
            assistant_msg = {"role": "assistant"}
            if content:
                assistant_msg["content"] = content
            if tool_calls:
                assistant_msg["tool_calls"] = tool_calls
                
            messages.append(assistant_msg)
            
            if tool_calls:
                # LLM requested tool execution
                for tcall in tool_calls:
                    tname = tcall.get("function", {}).get("name")
                    targs_str = tcall.get("function", {}).get("arguments", "{}")
                    
                    try:
                        targs = json.loads(targs_str) if isinstance(targs_str, str) else targs_str
                    except Exception:
                        targs = {}
                        
                    if self.bus:
                        self.bus.publish(EventContext(
                            event_name="ToolCalled",
                            timestamp=datetime.datetime.now().isoformat(),
                            source="AILoopEngine",
                            priority=EventPriority.NORMAL,
                            session_id=session_id,
                            payload={"tool_name": tname, "status": "running"}
                        ))
                    
                    needs_approval = tname in ["run_bash_command", "write_file", "edit_file_content"]
                    
                    if needs_approval and self.bus:
                        # Construct a dummy plan for ApprovalModal
                        from nexa.core.pipeline.execution.models import ExecutionPlan, ExecutionStage, CommandStep, ExecutionStrategy
                        
                        dummy_step = CommandStep(
                            id=f"tool_{iteration}",
                            executable=tname,
                            args=[json.dumps(targs)],
                            strategy=ExecutionStrategy.STOP_ON_ERROR,
                            raw_command=f"Tool Call: {tname}({json.dumps(targs, indent=2)})"
                        )
                        dummy_plan = ExecutionPlan(
                            stages=[ExecutionStage(name=f"Agent Tool Request: {tname}", steps=[dummy_step])],
                            can_rollback=False
                        )
                        
                        approval_event = threading.Event()
                        user_action = {"action": "no"}
                        
                        def on_approval_granted(ctx):
                            nonlocal user_action
                            if ctx.event_name == "ApprovalGranted":
                                user_action["action"] = "yes"
                                approval_event.set()
                        def on_planning_revision(ctx):
                            nonlocal user_action
                            if ctx.event_name == "PlanRevisionRequested":
                                user_action["action"] = "comment"
                                user_action["comment"] = ctx.payload.get("comment", "")
                                approval_event.set()
                        def on_approval_rejected(ctx):
                            nonlocal user_action
                            if ctx.event_name == "ApprovalRejected":
                                user_action["action"] = "no"
                                approval_event.set()
                        
                        self.bus.subscribe("ApprovalGranted", on_approval_granted)
                        self.bus.subscribe("PlanRevisionRequested", on_planning_revision)
                        self.bus.subscribe("ApprovalRejected", on_approval_rejected)
                        
                        try:
                            self.bus.publish_async(EventContext(
                                event_name="BeforeApproval",
                                timestamp=datetime.datetime.now().isoformat(),
                                source="AILoopEngine",
                                priority=EventPriority.HIGH,
                                session_id=session_id,
                                payload={"plan": dummy_plan, "tool_approval": True}
                            ))
                            
                            if self.bus:
                                self.bus.publish(EventContext(
                                    event_name="ToolCalled",
                                    timestamp=datetime.datetime.now().isoformat(),
                                    source="AILoopEngine",
                                    priority=EventPriority.NORMAL,
                                    session_id=session_id,
                                    payload={"tool_name": f"Awaiting approval for {tname}", "status": "running"}
                                ))
                            if not approval_event.wait(timeout=60.0):
                                user_action["action"] = "timeout"
                        finally:
                            self.bus.unsubscribe("ApprovalGranted", on_approval_granted)
                            self.bus.unsubscribe("PlanRevisionRequested", on_planning_revision)
                            self.bus.unsubscribe("ApprovalRejected", on_approval_rejected)
                        
                        if user_action["action"] == "yes":
                            if self.bus:
                                self.bus.publish(EventContext(
                                    event_name="ToolCalled",
                                    timestamp=datetime.datetime.now().isoformat(),
                                    source="AILoopEngine",
                                    priority=EventPriority.NORMAL,
                                    session_id=session_id,
                                    payload={"tool_name": tname, "status": "success"}
                                ))
                            result_str = str(registry.execute(tname, targs))
                        elif user_action["action"] == "comment":
                            if self.bus:
                                self.bus.publish(EventContext(
                                    event_name="ToolCalled",
                                    timestamp=datetime.datetime.now().isoformat(),
                                    source="AILoopEngine",
                                    priority=EventPriority.NORMAL,
                                    session_id=session_id,
                                    payload={"tool_name": tname, "status": "error"}
                                ))
                            result_str = f"Execution aborted. User commented: {user_action['comment']}"
                        else:
                            if self.bus:
                                self.bus.publish(EventContext(
                                    event_name="ToolCalled",
                                    timestamp=datetime.datetime.now().isoformat(),
                                    source="AILoopEngine",
                                    priority=EventPriority.NORMAL,
                                    session_id=session_id,
                                    payload={"tool_name": tname, "status": "error"}
                                ))
                            if user_action.get("action") == "timeout":
                                result_str = "Execution aborted due to timeout."
                            else:
                                result_str = "Execution aborted by user."
                    else:
                        # Auto-execute safe tools
                        if self.bus:
                            self.bus.publish(EventContext(
                                event_name="ToolCalled",
                                timestamp=datetime.datetime.now().isoformat(),
                                source="AILoopEngine",
                                priority=EventPriority.NORMAL,
                                session_id=session_id,
                                payload={"tool_name": tname, "status": "success"}
                            ))
                        result_str = str(registry.execute(tname, targs))
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tcall.get("id", ""),
                        "name": tname,
                        "content": result_str
                    })
            else:
                # No tool calls, assume LLM provided the final plan
                final_json_content = content
                break
                
        if not final_json_content:
            return PlannerReport(success=False, error_message=f"Agent loop exhausted max iterations ({max_iterations}) without reaching a final plan.")
            
        # Parse final plan JSON
        try:
            if "```json" in final_json_content:
                final_json_content = final_json_content.split("```json")[1].split("```")[0].strip()
            elif "```" in final_json_content:
                final_json_content = final_json_content.split("```")[1].strip()
                
            data = json.loads(final_json_content)
            
            from nexa.core.ai.planner.schema import WorkItem, AcceptanceCriterion, RiskItem
            
            work_items = []
            for wi in data.get("work_items", []):
                work_items.append(WorkItem(
                    title=wi.get("title", ""),
                    description=wi.get("description", ""),
                    affected_files=wi.get("affected_files", []),
                    objective=wi.get("objective", "")
                ))
                
            ac = []
            for a in data.get("acceptance_criteria", []):
                ac.append(AcceptanceCriterion(
                    description=a.get("description", ""),
                    priority=a.get("priority", "MUST"),
                    verification_method=a.get("verification_method", "")
                ))
                
            ra = []
            for r in data.get("risk_analysis", []):
                ra.append(RiskItem(
                    category=r.get("category", "General"),
                    probability=r.get("probability", "MEDIUM"),
                    impact=r.get("impact", "MEDIUM"),
                    mitigation=r.get("mitigation", "")
                ))
                
            validated_plan = PlanningResult(
                goal=context.user_goal,
                summary=data.get("summary", "Agent Loop completed successfully."),
                objective=data.get("objective", ""),
                constraints=data.get("constraints", []),
                work_items=work_items,
                acceptance_criteria=ac,
                risk_analysis=ra,
                clarifications=data.get("clarifications", []),
                confidence=ConfidenceAssessment(level="HIGH", score=100, reason="Iterative tool usage", missing_information="")
            )
            
            if self.bus:
                self.bus.publish(EventContext(
                    event_name="AfterPlanning",
                    timestamp=datetime.datetime.now().isoformat(),
                    source="AILoopEngine",
                    priority=EventPriority.NORMAL,
                    session_id=session_id,
                    duration=time.time() - start_time,
                    payload={"plan": validated_plan}
                ))
                
            return PlannerReport(success=True, error_message="", plan=validated_plan)
        except Exception as e:
            return PlannerReport(success=False, error_message=f"Failed to parse final plan JSON: {e}\nRaw Content:\n{final_json_content}")
