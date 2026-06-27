from typing import List
from .models import KnowledgeFile, IntentContext
from .graph import DependencyGraph

class FileScorer:
    """
    Computes a numerical score breakdown for each file based on advanced heuristics.
    """
    def score(self, files: List[KnowledgeFile], graph: DependencyGraph, intent: IntentContext) -> None:
        for f in files:
            breakdown = {
                "goal_match": 0.0,
                "dependency": 0.0,
                "analyzer": 0.0,
                "filename": 0.0,
                "framework": 0.0,
                "folder": 0.0
            }
            
            # 1. Goal Match (from selection reasons)
            for reason in f.selection_reason:
                if "Goal keyword matched" in reason:
                    breakdown["goal_match"] += 20.0
                    
            # 2. Dependency Score
            node = graph.get_node(f.path)
            if node:
                # Based on out-degree
                breakdown["dependency"] += len(node.dependencies) * 2.0
                
            # 3. Filename Match (if filename contains any keyword)
            path_lower = f.path.lower()
            for kw in intent.keywords:
                if kw in path_lower.split("/")[-1]:
                    breakdown["filename"] += 15.0
                    
            # 4. Folder structure (if it's in a core domain folder)
            if intent.domain != "general" and intent.domain in path_lower:
                breakdown["folder"] += 10.0
                
            # Cap sub-scores
            breakdown["goal_match"] = min(breakdown["goal_match"], 40.0)
            breakdown["dependency"] = min(breakdown["dependency"], 20.0)
            breakdown["filename"] = min(breakdown["filename"], 20.0)
            
            f.score_breakdown = breakdown
            f.score = sum(breakdown.values())
