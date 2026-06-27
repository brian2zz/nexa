from .context import PromptContext
from .formatter import PromptFormatter
from .templates import TASK_TEMPLATES

class PromptBuilder:
    def build_user_prompt(self, context: PromptContext) -> str:
        """
        Builds the raw string for the user prompt using the formatter.
        """
        formatter = PromptFormatter()

        # Project Section
        formatter.add_section("PROJECT")
        if context.framework or context.language or context.architecture:
            formatter.add_text(f"Framework: {context.framework}")
            formatter.add_text(f"Language: {context.language}")
            formatter.add_text(f"Architecture: {context.architecture}")
        
        if context.project_health:
            formatter.add_text(f"Project Health: {context.project_health}")
            formatter.add_text(f"Risk Score: {context.risk_score}")

        if context.statistics:
            formatter.add_text("Statistics:")
            formatter.add_table(context.statistics)

        if context.warnings:
            formatter.add_warning(context.warnings)

        # Goal Section
        if context.goal:
            formatter.add_section("GOAL")
            formatter.add_text(context.goal)

        # Important Files Section
        if context.important_files:
            formatter.add_section("IMPORTANT FILES")
            formatter.add_list(context.important_files)

        # Source Code Section
        if context.selected_files:
            formatter.add_section("SOURCE CODE")
            for sf in context.selected_files:
                path = sf.get("path", "Unknown File")
                content = sf.get("content", "")
                formatter.add_text(f"File: {path}")
                formatter.add_code(content)

        # Task Section
        formatter.add_section("TASK")
        task_instruction = TASK_TEMPLATES.get(context.task.lower(), context.task)
        formatter.add_text(task_instruction)

        return formatter.build()
