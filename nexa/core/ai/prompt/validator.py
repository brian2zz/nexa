from .context import PromptContext

class PromptValidator:
    def validate(self, context: PromptContext) -> None:
        """
        Validates the PromptContext before building.
        Raises ValueError if validation fails.
        """
        if not context.goal and not context.task:
            raise ValueError("Validation Failed: Both goal and task cannot be empty.")
            
        if not context.framework:
            # We can log a warning or raise depending on strictness
            pass
            
        # Check source size roughly
        total_source_length = sum(len(f.get("content", "")) for f in context.selected_files)
        # Assuming ~4 characters per token, this checks if source is > ~50k tokens roughly
        if total_source_length > 200000:
            raise ValueError("Validation Failed: Selected source code is too large. Please narrow down selected files.")
