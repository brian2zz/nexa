import concurrent.futures
from typing import List, Dict, Any, Callable
from nexa.core.agent.tools.models import KnowledgeRequest, ToolMetadata
from nexa.core.agent.tools.strategies import BasePriorityStrategy, Balanced
from nexa.core.agent.tools.registry import ToolRegistry

class ToolPrioritizer:
    """
    Context Workflow Orchestrator. 
    Intercepts KnowledgeRequests and orchestrates multiple read-only tools to gather context.
    """
    def __init__(self, registry: ToolRegistry, strategy: BasePriorityStrategy = None):
        self.registry = registry
        self.strategy = strategy or Balanced()
        self._cache: Dict[str, List[str]] = {}

    def _get_relevant_tools(self, request: KnowledgeRequest) -> List[ToolMetadata]:
        need = request.need.lower()
        
        all_metadata = list(self.registry.get_all_metadata().values())
        relevant = []
        
        for meta in all_metadata:
            # security boundary: strict read_only=True
            if not meta.read_only:
                continue
                
            # match capability
            if need in [c.lower() for c in meta.capabilities]:
                relevant.append(meta)
                
        # Hard Reject if empty or accidentally included non-readonly (though caught above)
        if any(not m.read_only for m in relevant):
             raise PermissionError("FATAL: ToolPrioritizer intercepted a Write Tool. This is strictly prohibited in the Knowledge Acquisition Pipeline.")
                
        # fallback if no exact capability match (e.g., return fundamental read tools)
        if not relevant:
            relevant = [m for m in all_metadata if m.category in ["general", "search"] and m.read_only]
            
        return relevant

    def _execute_tool(self, tool_name: str, kwargs: dict) -> str:
        try:
             result = self.registry.execute(tool_name, kwargs)
             return f"--- [{tool_name}] ---\n{result}\n"
        except Exception as e:
             return f"--- [{tool_name}] ERROR ---\n{str(e)}\n"

    def resolve_knowledge_request(self, request: KnowledgeRequest, context_kwargs: dict = None) -> str:
        """
        Executes the prioritized tools and returns the combined context blob.
        """
        context_kwargs = context_kwargs or {}
        cache_key = f"{request.intent_domain}:{request.need}"
        
        tool_names_to_run = []
        if cache_key in self._cache:
             tool_names_to_run = self._cache[cache_key]
        else:
             relevant_tools = self._get_relevant_tools(request)
             prioritized_tools = self.strategy.sort_tools(relevant_tools)
             tool_names_to_run = [t.name for t in prioritized_tools]
             # save to cache
             self._cache[cache_key] = tool_names_to_run
             
        if not tool_names_to_run:
            return "No context could be gathered for this request."

        # Parallel Execution of Context Gathering
        combined_context = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_tool = {
                executor.submit(self._execute_tool, name, context_kwargs.get(name, {})): name 
                for name in tool_names_to_run
            }
            for future in concurrent.futures.as_completed(future_to_tool):
                tool_name = future_to_tool[future]
                try:
                    data = future.result()
                    combined_context.append(data)
                except Exception as exc:
                    combined_context.append(f"--- [{tool_name}] ERROR ---\n{exc}\n")
                    
        return "\n".join(combined_context)
