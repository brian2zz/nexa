from .base import BasePromptBuilder
import json

class RepairPromptBuilder(BasePromptBuilder):
    def build_system_prompt(self, request) -> str:
        if request.system_override:
            return request.system_override
            
        facts = request.context_bundle.get("project_facts", {})
        language = facts.get("language", "Unknown")
        
        return (
            f"You are a Nexa AI Repair Engine. Your task is to FIX bugs in {language} code.\n"
            "Rules:\n"
            "1. Analyze the stacktrace or error description provided.\n"
            "2. Identify the root cause in the GIVEN CONTEXT.\n"
            "3. Output the FIXED code enclosed in a markdown block.\n"
            "4. Briefly explain what was wrong before the code block if necessary, but keep it minimal.\n"
        )
        
    def build_user_prompt(self, request) -> str:
        plan_str = json.dumps(request.execution_plan, indent=2)
        context_str = self.build_context_block(request.context_bundle)
        
        prompt = (
            f"Repair Plan / Error Info:\n{plan_str}\n\n"
            f"{context_str}\n"
        )
        if request.user_instruction:
            prompt += f"\nError Details / Instruction: {request.user_instruction}\n"
            
        prompt += "\nPlease fix the code and output the working version."
        return prompt
