import json
import datetime
from typing import Optional, Callable, Any
from nexa.core.events.bus import PipelineBus, EventContext
from nexa.core.models.enums import EventPriority

_BUS: Optional[PipelineBus] = None
_SESSION_ID_FN: Optional[Callable[[], Any]] = None

def set_pipeline_bus(bus: PipelineBus, session_id_fn: Optional[Callable[[], Any]] = None):
    global _BUS, _SESSION_ID_FN
    _BUS = bus
    _SESSION_ID_FN = session_id_fn

def submit_execution_plan(plan_json: str) -> str:
    """
    Satu-satunya jembatan LLM menuju Pipeline Modifikasi (Write).
    LLM memanggil tool ini ketika ia sudah selesai berpikir dan menyusun ExecutionPlan.
    """
    try:
        plan = json.loads(plan_json) if isinstance(plan_json, str) else plan_json
        if not isinstance(plan, dict):
            return "Error: ExecutionPlan must be a valid JSON object."
        if "files" not in plan:
            return "Error: ExecutionPlan must contain a 'files' array."
            
        if not _BUS:
            return "Error: Pipeline bus not initialized."

        session_id = _SESSION_ID_FN() if _SESSION_ID_FN and callable(_SESSION_ID_FN) else 0

        _BUS.publish(EventContext(
            event_name="ExecutionPlanSubmitted",
            timestamp=datetime.datetime.now().isoformat(),
            source="LLMTool:submit_execution_plan",
            priority=EventPriority.HIGH,
            session_id=session_id,
            payload={"plan": plan, "files": plan.get("files", [])}
        ))
        
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

def register_pipeline_tools(registry, bus: Optional[PipelineBus] = None, session_id_fn: Optional[Callable[[], Any]] = None):
    if bus:
        set_pipeline_bus(bus, session_id_fn)
    registry.register("submit_execution_plan", submit_execution_plan, SUBMIT_PLAN_SCHEMA)

