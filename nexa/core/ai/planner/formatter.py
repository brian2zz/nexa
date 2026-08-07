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
        md = f"## {plan.goal}\n\n"
        md += f"{plan.summary}\n\n"
        
        md += f"### 🎯 Objective\n"
        md += f"{plan.objective}\n\n"
        
        md += f"### Metadata\n"
        md += f"- **Confidence:** {plan.confidence.level} ({plan.confidence.score}%)\n"
        md += f"  - *Reason:* {plan.confidence.reason}\n"
        if plan.confidence.missing_information:
            md += f"  - *Missing Info:* {plan.confidence.missing_information}\n"
        md += "\n"
        
        if plan.constraints:
            md += "### 🚫 Constraints\n"
            for c in plan.constraints:
                md += f"- {c}\n"
            md += "\n"
            
        md += "### 🧩 Affected Components\n"
        ac = plan.affected_components
        if ac.models: md += f"- **Models:** {', '.join(ac.models)}\n"
        if ac.services: md += f"- **Services:** {', '.join(ac.services)}\n"
        if ac.commands: md += f"- **Commands:** {', '.join(ac.commands)}\n"
        if ac.tests: md += f"- **Tests:** {', '.join(ac.tests)}\n"
        if ac.docs: md += f"- **Docs:** {', '.join(ac.docs)}\n"
        if ac.files: md += f"- **Files:** {', '.join(ac.files)}\n"
        md += "\n"
        
        md += "### 📋 Work Items\n"
        for i, w in enumerate(plan.work_items, 1):
            md += f"**{i}. {w.title}**\n"
            md += f"  - *Objective:* {w.objective}\n"
            md += f"  - *Description:* {w.description}\n"
            if w.affected_files:
                md += f"  - *Files:* {', '.join(w.affected_files)}\n"
        md += "\n"
        
        if plan.acceptance_criteria:
            md += "### ✅ Acceptance Criteria\n"
            for i, a in enumerate(plan.acceptance_criteria, 1):
                md += f"- **[{a.priority}]** {a.description}\n"
                md += f"  *Verification:* {a.verification_method}\n"
            md += "\n"
            
        if plan.risk_analysis:
            md += "### [!] Risk Analysis\n\n"
            for r in plan.risk_analysis:
                md += f"- **{r.category}** (Prob: {r.probability}, Impact: {r.impact})\n"
                md += f"  - *Mitigation:* {r.mitigation}\n"
            md += "\n"
            
        return md
