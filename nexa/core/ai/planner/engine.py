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
            "Your ONLY responsibility is to create a PlanningResult in STRICT JSON format.\n"
            "You DO NOT write code directly, you DO NOT execute commands. You only output a software design blueprint JSON with objectives, work items, and risks.\n\n"
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
            "You MUST return a JSON object representing a PlanningResult.\n"
            "{\n"
            "  \"goal\": \"string (Describe what you were asked to do)\",\n"
            "  \"summary\": \"string (Provide your detailed final answer, search results, or findings here)\",\n"
            "  \"objective\": \"string (The primary software engineering objective)\",\n"
            "  \"constraints\": [\"string (e.g. Don't modify auth, Backward compatible)\"],\n"
            "  \"affected_components\": {\n"
            "    \"models\": [\"string\"],\n"
            "    \"services\": [\"string\"],\n"
            "    \"commands\": [\"string\"],\n"
            "    \"tests\": [\"string\"],\n"
            "    \"docs\": [\"string\"],\n"
            "    \"files\": [\"string\"]\n"
            "  },\n"
            "  \"work_items\": [\n"
            "    {\n"
            "      \"title\": \"string (Task title)\",\n"
            "      \"description\": \"string (Detailed explanation of what needs to be built)\",\n"
            "      \"affected_files\": [\"string (Files needed to be modified for this item)\"],\n"
            "      \"objective\": \"string (The goal of this specific work item)\"\n"
            "    }\n"
            "  ],\n"
            "  \"acceptance_criteria\": [\n"
            "    {\n"
            "      \"description\": \"string (Condition that must be met)\",\n"
            "      \"priority\": \"MUST|SHOULD|COULD\",\n"
            "      \"verification_method\": \"string (How to test this, e.g. Unit test, Manual UI check)\"\n"
            "    }\n"
            "  ],\n"
            "  \"risk_analysis\": [\n"
            "    {\n"
            "      \"category\": \"Performance|Compatibility|Security|Rollback|Business\",\n"
            "      \"probability\": \"LOW|MEDIUM|HIGH\",\n"
            "      \"impact\": \"LOW|MEDIUM|HIGH\",\n"
            "      \"mitigation\": \"string (How to mitigate this risk)\"\n"
            "    }\n"
            "  ],\n"
            "  \"confidence\": {\n"
            "    \"level\": \"LOW|MEDIUM|HIGH\",\n"
            "    \"score\": 0, // integer 0-100\n"
            "    \"reason\": \"string (Why this confidence level)\",\n"
            "    \"missing_information\": \"string (What is still unknown)\"\n"
            "  }\n"
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

    def plan(self, context: PlannerContext, session_id: int = 0) -> PlannerReport:
        start_time = time.time()
        timestamp = datetime.datetime.now().isoformat()

        # Hierarchical Memory
        from nexa.core.ai.memory.hierarchical import HierarchicalMemory
        hm = HierarchicalMemory(session_id=session_id)
        memory_context = hm.build_context_for_llm(project_path=context.project_path)
        if memory_context:
            context = PlannerContext(
                project_path=context.project_path,
                knowledge_context=context.knowledge_context + "\n" + memory_context,
                project_facts=context.project_facts,
                pinned_memory=context.pinned_memory,
                conversation_memory=context.conversation_memory,
                user_goal=context.user_goal
            )

        if self.bus:
            self.bus.publish(EventContext(
                event_name="BeforePlanning",
                timestamp=timestamp,
                source="PlannerEngine",
                priority=EventPriority.NORMAL,
                session_id=session_id,
                payload={"goal": context.user_goal}
            ))

        # ─────────────────────────────────────────────────────────────
        # COGNITIVE PIPELINE (Priority Sovereign Order)
        # ─────────────────────────────────────────────────────────────

        from nexa.core.ai.cognitive.engines.intent_resolver import IntentResolver
        from nexa.core.ai.knowledge.orchestrator import KnowledgeOrchestrator, CapabilityResolver
        from nexa.core.ai.cognitive.engines.hypothesis import HypothesisEngine
        from nexa.core.ai.cognitive.engines.reasoning import ReasoningEngine
        from nexa.core.ai.cognitive.engines.planning import PlanningEngine

        # ── STEP 1: IntentResolver → Need[]  (Rule Engine, no LLM)
        print("       [Cognitive Layer] Resolving Intent -> Needs...")
        intent_resolver = IntentResolver()
        needs = intent_resolver.resolve(context.user_goal)
        print(f"       [Cognitive Layer] Needs: {[n.value for n in needs]}")

        # ── STEP 2: HypothesisEngine → HypothesisResult  (LLM #1, tools=[])
        print("       [Cognitive Layer] Generating Hypotheses to guide search...")
        hypothesis_engine = HypothesisEngine()
        hypothesis_result = hypothesis_engine.generate(
            user_goal=context.user_goal,
            project_facts=context.project_facts,
            conversation_memory=context.conversation_memory,
        )
        hm.working.set("hypotheses", [h.get("description","") for h in hypothesis_result.hypotheses])
        hm.session.record("hypothesis",
            f"Generated {len(hypothesis_result.hypotheses)} hypotheses for: {context.user_goal[:80]}")

        # Extract search targets from hypotheses to enrich hints
        hypothesis_hints = {}
        for h in hypothesis_result.hypotheses:
            targets = h.get("search_targets", [])
            for t in targets:
                if "." in t:
                    hypothesis_hints["file_name"] = t
                    hypothesis_hints["target_file"] = t
                else:
                    hypothesis_hints["search_query"] = t
                    hypothesis_hints["keyword"] = t

        # ── STEP 3: KnowledgeOrchestrator → EvidenceBundle  (ONLY tool caller)
        print("       [Cognitive Layer] Knowledge Orchestrator acquiring evidence...")
        hints = CapabilityResolver.build_hints(
            context.user_goal, needs, project_facts=context.project_facts
        )
        hints.update(hypothesis_hints)

        orchestrator = KnowledgeOrchestrator(
            workspace_path=context.project_path,
            tool_budget=5
        )
        evidence_bundle = orchestrator.gather(needs, context_hints=hints)
        print(f"       [Cognitive Layer] Evidence: {len(evidence_bundle.needs_satisfied)} satisfied, "
              f"{len(evidence_bundle.needs_failed)} gaps, "
              f"{evidence_bundle.tool_calls_used}/{evidence_bundle.tool_budget} budget used")

        hm.working.set("needs", [n.value for n in needs])
        hm.working.set("evidence_satisfied", evidence_bundle.needs_satisfied)
        hm.working.set("evidence_gaps", evidence_bundle.needs_failed)
        hm.session.record("acquisition",
            f"Evidence: {len(evidence_bundle.needs_satisfied)} satisfied, "
            f"{len(evidence_bundle.needs_failed)} gaps")

        # ── STEP 4: ReasoningEngine → ReasoningResult  (LLM #2, tools=[])
        print("       [Cognitive Layer] Reasoning & Validating Evidence...")
        reasoning_engine = ReasoningEngine()
        reasoning_result = reasoning_engine.analyze(
            evidence_bundle=evidence_bundle,
            user_goal=context.user_goal,
            hypotheses=hypothesis_result
        )
        hm.working.set("root_cause", reasoning_result.root_cause[:200] if reasoning_result.root_cause else "")
        hm.session.record("reasoning",
            f"Root Cause (confidence {reasoning_result.confidence}%): {reasoning_result.root_cause[:150]}")

        # ── STEP 5: PlanningEngine → PlanningResult  (LLM #3, tools=[])
        print("       [Cognitive Layer] Formulating Execution Plan...")
        planning_engine = PlanningEngine()
        plan = planning_engine.build(reasoning_result, context.user_goal)

        success, error, validated_plan = self.validator.validate_dataclass(plan)

        # Flush Working Memory → Session Trail
        hm.flush_working_to_session(goal_summary=context.user_goal[:60])

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
                payload={
                    "plan": validated_plan,
                    "confidence": reasoning_result.confidence,
                    "evidence_gaps": evidence_bundle.needs_failed
                }
            ))

        return PlannerReport(success=True, error_message="", plan=validated_plan)


