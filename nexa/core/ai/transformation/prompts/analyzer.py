from .base import BasePromptBuilder
import json

class AnalyzerPromptBuilder(BasePromptBuilder):
    def build_system_prompt(self, request) -> str:
        if request.system_override:
            return request.system_override
            
        facts = request.context_bundle.get("project_facts", {})
        language = facts.get("language", "Unknown")
        mode = request.mode.value.upper()
        
        return (
            f"You are a Nexa AI {mode} Engine.\n"
            f"Project Environment: {language}.\n"
            "Rules:\n"
            "1. Read the provided GIVEN CONTEXT carefully.\n"
            "2. Provide a clear, concise, and professional explanation/summary.\n"
            "3. Use markdown formatting for readability.\n"
            "4. Do NOT output a new code block unless providing small examples.\n"
        )
        
    def build_user_prompt(self, request) -> str:
        context_str = self.build_context_block(request.context_bundle)
        
        prompt = f"{context_str}\n"
        if request.user_instruction:
            prompt += f"\nInstruction: {request.user_instruction}\n"
        else:
            prompt += "\nPlease analyze and explain the provided code."
            
        return prompt
