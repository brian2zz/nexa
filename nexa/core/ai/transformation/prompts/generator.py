from .base import BasePromptBuilder
import json

class GeneratorPromptBuilder(BasePromptBuilder):
    def build_system_prompt(self, request) -> str:
        if request.system_override:
            return request.system_override
            
        facts = request.context_bundle.get("project_facts", {})
        language = facts.get("language", "Unknown")
        framework = facts.get("framework", "Unknown")
        
        return (
            f"You are a Nexa AI Generator Engine. Your task is to GENERATE new code from scratch.\n"
            f"Project Environment: {language} with {framework}.\n"
            "Rules:\n"
            "1. You MUST output ONLY valid code enclosed in markdown block (```language ... ```).\n"
            "2. DO NOT write conversational text outside the block.\n"
            "3. Ensure the generated code fits the provided context architecture.\n"
        )
        
    def build_user_prompt(self, request) -> str:
        plan_str = json.dumps(request.execution_plan, indent=2)
        context_str = self.build_context_block(request.context_bundle)
        
        prompt = (
            f"Execution Plan:\n{plan_str}\n\n"
            f"{context_str}\n"
        )
        if request.user_instruction:
            prompt += f"\nUser Instruction: {request.user_instruction}\n"
            
        prompt += "\nPlease generate the required file exactly as instructed in the Execution Plan."
        return prompt
