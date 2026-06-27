import json
from .schema import ExecutionPlan

class PlanFormatter:
    """
    Formats an ExecutionPlan into different representations.
    """
    def to_json(self, plan: ExecutionPlan, pretty=True) -> str:
        # Convert dataclass to dict via __dict__ logic or specific mapping
        # Since we just want representation, we can build a dict
        data = {
            "goal": plan.goal,
            "summary": plan.summary,
            "complexity": plan.complexity,
            "estimated_time": plan.estimated_time,
            "risk": plan.risk,
            "affected_modules": plan.affected_modules,
            "affected_files": plan.affected_files,
            "files_to_create": plan.files_to_create,
            "files_to_modify": plan.files_to_modify,
            "dependencies": plan.dependencies,
            "execution_steps": [{"action": s.action, "target": s.target, "description": s.description} for s in plan.execution_steps],
            "verification_steps": plan.verification_steps,
            "warnings": plan.warnings,
            "recommendations": plan.recommendations,
            "rollback_strategy": plan.rollback_strategy,
            "confidence": plan.confidence
        }
        return json.dumps(data, indent=2 if pretty else None)

    def to_markdown(self, plan: ExecutionPlan) -> str:
        md = f"## Execution Plan: {plan.goal}\n\n"
        md += f"**Summary:** {plan.summary}\n\n"
        md += f"- **Complexity:** {plan.complexity}\n"
        md += f"- **Estimated Time:** {plan.estimated_time}\n"
        md += f"- **Risk:** {plan.risk}\n"
        md += f"- **Confidence:** {plan.confidence}%\n\n"
        
        if plan.files_to_create:
            md += "### 📄 Files to Create\n"
            for f in plan.files_to_create:
                md += f"- `{f}`\n"
            md += "\n"
            
        if plan.files_to_modify:
            md += "### 📝 Files to Modify\n"
            for f in plan.files_to_modify:
                md += f"- `{f}`\n"
            md += "\n"
            
        md += "### 🚀 Execution Steps\n"
        for i, step in enumerate(plan.execution_steps, 1):
            md += f"{i}. **[{step.action.upper()}]** `{step.target}` - {step.description}\n"
            
        if plan.warnings:
            md += "\n### ⚠️ Warnings\n"
            for w in plan.warnings:
                md += f"- {w}\n"
                
        if plan.recommendations:
            md += "\n### 💡 AI Recommendations (Review)\n"
            for r in plan.recommendations:
                md += f"- {r}\n"
                
        if plan.rollback_strategy:
            md += f"\n### ↩️ Rollback Strategy\n{plan.rollback_strategy}\n"
            
        return md
