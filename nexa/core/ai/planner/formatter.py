import json
from .schema import PlanningResult

class PlanFormatter:
    """
    Formats a PlanningResult into different representations.
    """
    def to_json(self, plan: PlanningResult, pretty=True) -> str:
        data = {
            "goal": plan.goal,
            "summary": plan.summary,
            "objective": plan.objective,
            "constraints": plan.constraints,
            "affected_components": {
                "models": plan.affected_components.models,
                "services": plan.affected_components.services,
                "commands": plan.affected_components.commands,
                "tests": plan.affected_components.tests,
                "docs": plan.affected_components.docs,
                "files": plan.affected_components.files
            },
            "work_items": [
                {
                    "title": w.title,
                    "description": w.description,
                    "affected_files": w.affected_files,
                    "objective": w.objective
                } for w in plan.work_items
            ],
            "acceptance_criteria": [
                {
                    "description": a.description,
                    "priority": a.priority,
                    "verification_method": a.verification_method
                } for a in plan.acceptance_criteria
            ],
            "risk_analysis": [
                {
                    "category": r.category,
                    "probability": r.probability,
                    "impact": r.impact,
                    "mitigation": r.mitigation
                } for r in plan.risk_analysis
            ],
            "confidence": {
                "level": plan.confidence.level,
                "score": plan.confidence.score,
                "reason": plan.confidence.reason,
                "missing_information": plan.confidence.missing_information
            }
        }
        return json.dumps(data, indent=2 if pretty else None)

    def to_markdown(self, plan: PlanningResult) -> str:
        # If summary is rich markdown containing blueprint sections, print it directly
        if "##" in plan.summary or "```" in plan.summary:
            md = f"{plan.summary}\n\n"
        else:
            md = f"## {plan.goal}\n\n"
            if plan.summary:
                md += f"{plan.summary}\n\n"
            if plan.objective:
                md += f"### 🎯 Objective\n{plan.objective}\n\n"
        
        if plan.work_items:
            md += "### 📋 Work Items\n"
            for i, w in enumerate(plan.work_items, 1):
                md += f"**{i}. {w.title}**\n"
                if w.objective:
                    md += f"  - *Objective:* {w.objective}\n"
                if w.description:
                    md += f"  - *Description:* {w.description}\n"
                if w.affected_files:
                    md += f"  - *Files:* {', '.join(w.affected_files)}\n"
            md += "\n"
        
        if plan.acceptance_criteria:
            md += "### ✅ Acceptance Criteria\n"
            for i, a in enumerate(plan.acceptance_criteria, 1):
                md += f"- **[{a.priority}]** {a.description}\n"
                if a.verification_method:
                    md += f"  *Verification:* {a.verification_method}\n"
            md += "\n"
            
        if plan.risk_analysis:
            md += "### [!] Risk Analysis\n"
            for r in plan.risk_analysis:
                md += f"- **{r.category}** (Prob: {r.probability}, Impact: {r.impact})\n"
                if r.mitigation:
                    md += f"  - *Mitigation:* {r.mitigation}\n"
            md += "\n"
            
        return md.strip()
