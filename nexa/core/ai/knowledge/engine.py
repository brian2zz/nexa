import time
from .models import ScannerResult, AnalyzerResult, KnowledgeContext
from .intent import IntentEngine
from .selector import CandidateSelector
from .dependency import DependencyParser
from .graph import DependencyGraph
from .scorer import FileScorer
from .ranking import RankingManager
from .optimizer import RuleBasedOptimizer
from .summarizer import RegexSummarizer
from .metrics import MetricsCalculator

class KnowledgeEngine:
    """
    Facade orchestrator for the Knowledge Engine pre-processing layer.
    """
    def __init__(self):
        self.intent_engine = IntentEngine()
        self.selector = CandidateSelector()
        self.dependency_parser = DependencyParser()
        self.scorer = FileScorer()
        self.ranking = RankingManager()
        self.optimizer = RuleBasedOptimizer(max_files=9)
        self.summarizer = RegexSummarizer()
        self.metrics = MetricsCalculator()

    def build(self, goal: str, task: str, scanner_result: ScannerResult, analyzer_result: AnalyzerResult) -> KnowledgeContext:
        start_time = time.time()
        
        # 1. Intent Analysis
        intent = self.intent_engine.analyze(goal)
        
        # 2. Selection
        candidates = self.selector.select(scanner_result, intent)
        
        # 3. Dependency Graph Construction
        graph = DependencyGraph()
        for c in candidates:
            graph.add_node(c.path)
            deps = self.dependency_parser.parse(c.content, analyzer_result.language, c.path)
            for target_name, rel_type in deps:
                graph.add_edge(c.path, target_name, rel_type)

        # 4. Scoring
        self.scorer.score(candidates, graph, intent)
        
        # 5. Ranking
        ranked = self.ranking.rank(candidates)
        
        # 6. Optimization (Caveman BaseOptimizer)
        final_files = self.optimizer.optimize(ranked)
        
        # 7. Summarization
        for f in final_files:
            f.summary = self.summarizer.summarize(f.content, analyzer_result.language, f.path)
            
        # 8. Metrics calculation
        # Cache hit rate is mocked here since we don't expose it directly yet from the parser
        report = self.metrics.calculate(scanner_result, final_files, graph, start_time)
        
        return KnowledgeContext(
            selected_files=final_files,
            selected_modules=[intent.domain] if intent.domain != "general" else [],
            dependency_graph=graph.nodes,
            ranking=[f.path for f in ranked],
            metrics=report,
            project_name=scanner_result.project_root,
            framework=analyzer_result.framework,
            language=analyzer_result.language
        )
