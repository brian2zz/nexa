from nexa.core.ai.planner.schema import ExecutionPlan, PlannerContext
from nexa.core.ai.providers.factory import ProviderFactory
import re

class AIGenerator:
    """
    The Maker. Given an ExecutionPlan and a target file, it generates the actual source code.
    """
    def __init__(self):
        pass

    def extract_code(self, text: str) -> str:
        # Find markdown code block
        match = re.search(r'```(?:[\w]+)?\n(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()

    def generate_file(self, plan: ExecutionPlan, context: PlannerContext, target_file: str, description: str) -> str:
        provider = ProviderFactory.create()
        
        sys_prompt = (
            "You are an AI Code Generator. Your task is to output the EXACT source code for a specific file.\n"
            "You must output ONLY the raw code inside a single markdown code block (```...```). Do not include any explanations.\n"
        )
        
        user_prompt = (
            f"Project: {context.project_path}\n"
            f"Goal: {plan.goal}\n"
            f"Target File: {target_file}\n"
            f"Instructions for this file: {description}\n\n"
        )
        
        if context.project_facts:
            user_prompt += f"Project Facts:\n{context.project_facts}\n\n"
        if context.pinned_memory:
            user_prompt += f"Pinned Rules:\n{context.pinned_memory}\n\n"
            
        user_prompt += "Please generate the complete, production-ready code for this file now."
        
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            raw_resp = provider.generate(messages, temperature=0.3)
            content = raw_resp.get("content", "") if isinstance(raw_resp, dict) else str(raw_resp)
            return self.extract_code(content)
        except Exception:
            return ""
