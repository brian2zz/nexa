SYSTEM_PROMPT_TEMPLATE = """You are an expert software architect.
You specialize in:
- Django
- Flutter
- NexaPHP
- React
- Laravel

Follow project architecture.
Never invent files.
Always explain reasoning.
"""

TASK_TEMPLATES = {
    "analyze": "Analyze the provided project context and source code. Provide strengths, weaknesses, risks, and recommendations.",
    "planner": "Generate a detailed implementation plan for the given goal based on the project context.",
    "code_review": "Review the selected source code for best practices, security issues, and performance optimizations.",
    "debug": "Identify the cause of the bug in the selected source code and propose a solution.",
    "explain": "Explain how the selected source code works in the context of the project architecture.",
    "refactor": "Refactor the selected source code to improve readability, maintainability, and alignment with the framework."
}
