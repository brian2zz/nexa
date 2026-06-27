from .base import BasePromptBuilder
import json

class ModifierPromptBuilder(BasePromptBuilder):
    def build_system_prompt(self, request) -> str:
        if request.system_override:
            return request.system_override
            
        facts = request.context_bundle.get("project_facts", {})
        language = facts.get("language", "Unknown")
        framework = facts.get("framework", "Unknown")
        
        mode = request.mode.value.upper()
        return (
            f"You are a Nexa AI Transformation Engine. Your task is to {mode} existing code.\n"
            f"Project Environment: {language} with {framework}.\n"
            "Rules:\n"
            "1. Read the provided GIVEN CONTEXT carefully.\n"
            "2. Modify the code according to the Execution Plan.\n"
            "3. You MUST output ONLY the final modified code enclosed in markdown block.\n"
            "4. Do NOT output partial patches, output the full modified file unless instructed otherwise.\n"
        )
        
    def build_user_prompt(self, request) -> str:
        plan_str = json.dumps(request.execution_plan, indent=2)
        context_str = self.build_context_block(request.context_bundle)
        
        prompt = (
            f"Execution Plan (Modifications required):\n{plan_str}\n\n"
            f"{context_str}\n"
        )
        if request.user_instruction:
            prompt += f"\nUser Instruction: {request.user_instruction}\n"
            
        prompt += "\nPlease provide the modified code."
        return prompt
