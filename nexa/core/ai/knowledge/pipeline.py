from typing import Optional
from nexa.core.agent.tools.prioritizer import ToolPrioritizer
from nexa.core.ai.context.builder import ContextBuilder
from nexa.core.ai.knowledge.intent import IntentEngine, IntentContext
from nexa.core.agent.tools.models import KnowledgeRequest

class KnowledgeAcquisitionPipeline:
    """
    The orchestrator for gathering context.
    Flow: Intent -> Prioritizer -> Knowledge Tools -> Context Builder -> [to Planner]
    """
    def __init__(self, prioritizer: ToolPrioritizer, builder: ContextBuilder, intent_engine: IntentEngine):
        self.prioritizer = prioritizer
        self.builder = builder
        self.intent_engine = intent_engine

    def acquire_context(self, user_goal: str, need: str, context_kwargs: dict = None) -> str:
        """
        Takes a user's goal and an abstract 'need' (e.g. 'git_context'),
        then orchestrates the read-only tools to gather data, returning a formatted string.
        """
        # 1. Intent Analysis
        intent_context: IntentContext = self.intent_engine.analyze(user_goal)
        
        # 2. Knowledge Request Mapping
        request = KnowledgeRequest(
            need=need,
            intent_domain=intent_context.domain
        )
        
        # 3. Prioritizer -> Tool Selector -> Execution (Read Only)
        # Note: prioritizer checks the read_only constraint
        raw_context = self.prioritizer.resolve_knowledge_request(request, context_kwargs=context_kwargs)
        
        # 4. Context Builder formats for the Planner
        final_prompt_context = self.builder.build_context(raw_context, user_goal)
        
        return final_prompt_context
