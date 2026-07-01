class ContextBuilder:
    """
    Formats and cleans the collected context from multiple read tools 
    before it is injected into the Planner's prompt.
    """
    
    def build_context(self, raw_knowledge: str, goal: str) -> str:
        """
        Takes the concatenated output from the Knowledge Acquisition Pipeline 
        and formats it into a clean, LLM-friendly prompt.
        """
        # We can add token truncation, formatting, or summarization here.
        # For now, we'll format it cleanly with clear boundaries.
        
        formatted = (
            "==================================================\n"
            "SYSTEM CONTEXT: GATHERED BY KNOWLEDGE ACQUISITION\n"
            "==================================================\n\n"
            f"User Goal: {goal}\n\n"
            "Below is the relevant information fetched automatically for you:\n"
            "--------------------------------------------------\n"
            f"{raw_knowledge.strip()}\n"
            "--------------------------------------------------\n\n"
            "Please use the above context to create your ExecutionPlan.\n"
            "You CANNOT run any terminal commands or write tools directly.\n"
        )
        
        return formatted
