import os
from unittest.mock import patch, MagicMock
from nexa.core.ai.planner.engine import AIPlannerEngine
from nexa.core.ai.planner.schema import PlannerContext

class TestPlannerIntegration:
    def test_planner_engine_end_to_end(self, tmpdir):
        # Create a mock workspace
        workspace = str(tmpdir)
        with open(os.path.join(workspace, "mocked_target.py"), "w") as f:
            f.write("def do_something():\n    pass")

        with patch('nexa.config.Config.get', return_value="mock"):
            planner = AIPlannerEngine()
            context = PlannerContext(
                user_goal="Fix the mocked target",
                project_path=workspace,
                project_facts={"language": "python"},
                knowledge_context="",
                pinned_memory=[],
                conversation_memory=[]
            )
            
            # The plan method should run the entire pipeline
            # IntentResolver -> Need[] -> HypothesisEngine -> KnowledgeOrchestrator -> ReasoningEngine -> PlanningEngine
            result = planner.plan(context)
            
            # If everything works correctly and mock schemas are parsed without errors,
            # it should return a valid PlanningResult with the mocked items.
            assert result.success is True
            assert result.plan is not None
            assert result.plan.objective == "Mocked plan objective"
            assert len(result.plan.work_items) == 1
            assert result.plan.work_items[0].title == "Mock Work Item"
            assert result.plan.confidence.level == "HIGH"
