from .context import PromptContext
from .messages import PromptMessages
from .optimizer import PromptOptimizer
from .validator import PromptValidator
from .builder import PromptBuilder
from .templates import SYSTEM_PROMPT_TEMPLATE

class PromptEngine:
    def __init__(self):
        self.optimizer = PromptOptimizer()
        self.validator = PromptValidator()
        self.builder = PromptBuilder()

    def create_messages(self, context: PromptContext) -> PromptMessages:
        """
        Orchestrates the entire prompt building pipeline:
        1. Optimize Context
        2. Validate Context
        3. Build String
        4. Wrap in PromptMessages
        """
        # Step 1: Optimize
        optimized_context = self.optimizer.optimize(context)
        
        # Step 2: Validate
        self.validator.validate(optimized_context)
        
        # Step 3: Build User Prompt
        user_prompt = self.builder.build_user_prompt(optimized_context)
        
        # Step 4: Construct Final Messages
        system_content = SYSTEM_PROMPT_TEMPLATE
        
        if optimized_context.caveman_level and optimized_context.caveman_level.lower() != "none":
            import os
            # Use relative path from this engine.py file up to caveman/skill.md
            current_dir = os.path.dirname(os.path.abspath(__file__))
            skill_path = os.path.join(current_dir, "..", "caveman", "skill.md")
            
            try:
                with open(skill_path, "r", encoding="utf-8") as f:
                    skill_rules = f.read()
                
                system_content += f"\n\n[CAVEMAN MODE: {optimized_context.caveman_level.lower()}]\n"
                system_content += "You must strictly follow the Caveman mode skill with the requested intensity level.\n\n"
                system_content += f"[CAVEMAN SKILL RULES]\n{skill_rules}\n"
            except Exception as e:
                # Fallback silently or log a warning if file not found
                system_content += f"\n\n[WARNING: Caveman mode requested but skill.md could not be loaded: {e}]"
                
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_prompt}
        ]
        
        # Estimate tokens roughly (chars / 4)
        est_tokens = sum(len(m["content"]) for m in messages) // 4
        
        # Extract selected files list for metadata
        file_list = [f.get("path") for f in optimized_context.selected_files if "path" in f]
        
        return PromptMessages(
            messages=messages,
            metadata={"optimized": True},
            estimated_tokens=est_tokens,
            selected_files=file_list,
            task=optimized_context.task,
            goal=optimized_context.goal
        )
