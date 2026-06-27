import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from nexa.core.ai.prompt import PromptEngine, PromptContext
import json

def test_prompt_builder():
    engine = PromptEngine()
    
    # 1. Create a dummy context
    context = PromptContext(
        task="analyze",
        goal="Improve authentication security",
        framework="Django",
        architecture="MVC",
        statistics={"total_files": 120, "lines_of_code": 15000},
        warnings=["Deprecation warning in views.py", "Unused import in urls.py"],
        important_files=["settings.py", "urls.py", "views.py"],
        selected_files=[
            {"path": "views.py", "content": "def login(request):\n    pass\n    "}
        ],
        caveman_level="ultra"
    )
    
    # 2. Build the messages
    result = engine.create_messages(context)
    
    # 3. Print the result nicely
    print("=== FINAL MESSAGES ===")
    print(json.dumps(result.messages, indent=2))
    
    print("\n=== METADATA ===")
    print(f"Tokens (est): {result.estimated_tokens}")
    print(f"Selected Files: {result.selected_files}")
    print(f"Task: {result.task}")
    print(f"Goal: {result.goal}")

if __name__ == "__main__":
    test_prompt_builder()
