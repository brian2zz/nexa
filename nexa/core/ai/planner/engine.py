import json
from typing import Dict, Any
from nexa.core.ai.providers.factory import ProviderFactory
from .schema import PlannerContext
from .validator import PlanValidator
from .report import PlannerReport

class AIPlannerEngine:
    """
    The orchestrator that generates Execution Plans based on deep context.
    """
    def __init__(self):
        self.validator = PlanValidator()

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
            "}\n"
            "\nCRITICAL INSTRUCTION: Return ONLY the raw JSON object. Do not wrap it in markdown code blocks if possible, or if you do, ensure it is ONLY valid JSON."
        )
        return prompt

    def plan(self, context: PlannerContext) -> PlannerReport:
        try:
            provider = ProviderFactory.create()
        except Exception as e:
            return PlannerReport(success=False, error_message=f"Provider Error: {e}")

        sys_prompt = self.build_system_prompt(context)
        
        # Build chat memory context
        messages = [{"role": "system", "content": sys_prompt}]
        for msg in context.conversation_memory:
            messages.append(msg)
            
        messages.append({"role": "user", "content": f"Create an ExecutionPlan for this goal: {context.user_goal}"})
        
        try:
            # Note: We can pass response_format={"type": "json_object"} if the provider supports it.
            # For now, we rely on prompt constraints + validator fallback.
            raw_resp = provider.generate(messages)
            content = raw_resp.get("content", "") if isinstance(raw_resp, dict) else str(raw_resp)
        except Exception as e:
            return PlannerReport(success=False, error_message=f"Generation Error: {e}")
            
        success, error, plan = self.validator.validate(content)
        if not success:
            return PlannerReport(success=False, error_message=error)
            
        return PlannerReport(success=True, error_message="", plan=plan)
