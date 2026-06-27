from .context import PromptContext

class PromptOptimizer:
    def optimize(self, context: PromptContext) -> PromptContext:
        """
        Cleans and optimizes the PromptContext before building the prompt.
        """
        # Limit the number of warnings to prevent blowing up the context window
        MAX_WARNINGS = 10
        if len(context.warnings) > MAX_WARNINGS:
            context.warnings = context.warnings[:MAX_WARNINGS]
            context.warnings.append(f"... and {len(context.warnings) - MAX_WARNINGS} more warnings omitted.")

        # Limit the number of important files
        MAX_FILES = 15
        if len(context.important_files) > MAX_FILES:
            context.important_files = context.important_files[:MAX_FILES]
            context.important_files.append(f"... and {len(context.important_files) - MAX_FILES} more important files omitted.")

        # Basic cleanup of source code (e.g., stripping trailing whitespaces)
        for sf in context.selected_files:
            if "content" in sf:
                sf["content"] = sf["content"].strip()

        return context
