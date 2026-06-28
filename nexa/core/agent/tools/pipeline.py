import json

def submit_execution_plan(plan_json: str) -> str:
    """
    Satu-satunya jembatan LLM menuju Pipeline Modifikasi (Write).
    LLM memanggil tool ini ketika ia sudah selesai berpikir dan menyusun ExecutionPlan.
    """
    try:
        # Validasi struktur minimal (untuk simulasi Sprint 3)
        plan = json.loads(plan_json)
        if "files" not in plan:
            return "Error: ExecutionPlan must contain a 'files' array."
            
        # Di Sprint berikutnya, data ini akan dilemparkan ke:
        # PipelineBus.publish(EventContext(event_name="ExecutionPlanSubmitted", payload=plan))
        # Yang kemudian membangunkan TransformationEngine dkk.
        
        return "SUCCESS: ExecutionPlan submitted. The Pipeline has taken over the execution."
        
    except Exception as e:
        return f"Error parsing ExecutionPlan: {e}"

SUBMIT_PLAN_SCHEMA = {
    "type": "function",
    "function": {
        "name": "submit_execution_plan",
        "description": "Submit the final ExecutionPlan when you are ready to modify files. You CANNOT modify files directly. You MUST use this tool.",
        "parameters": {
            "type": "object",
            "properties": {
                "plan_json": {
                    "type": "string", 
                    "description": "A JSON string representing the ExecutionPlan (must contain a 'files' array)"
                }
            },
            "required": ["plan_json"]
        }
    }
}

def register_pipeline_tools(registry):
    registry.register("submit_execution_plan", submit_execution_plan, SUBMIT_PLAN_SCHEMA)
