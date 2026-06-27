import time
from typing import List
from .models import KnowledgeFile, ScannerResult, KnowledgeReport
from .graph import DependencyGraph

class MetricsCalculator:
    """
    Calculates statistics and metrics into a comprehensive KnowledgeReport.
    """
    def calculate(self, 
                  initial_result: ScannerResult, 
                  final_files: List[KnowledgeFile], 
                  graph: DependencyGraph,
                  start_time: float,
                  cache_hit_count: int = 0,
                  cache_total_count: int = 1) -> KnowledgeReport:
        
        report = KnowledgeReport()
        
        initial_count = len(initial_result.files)
        final_count = len(final_files)
        
        report.project_files = initial_count
        report.selected_files = final_count
        report.ignored_files = initial_count - final_count
        
        if initial_count > 0:
            report.compression_ratio = ((initial_count - final_count) / initial_count) * 100.0
            
        total_size = 0
        largest = 0
        
        for f in final_files:
            size = len(f.content)
            total_size += size
            if size > largest:
                largest = size
                
        report.largest_file = largest
        if final_count > 0:
            report.average_file_size = total_size / final_count
            
        # Graph metrics
        nodes_len = len(graph.nodes)
        edges_len = sum(len(n.dependencies) for n in graph.nodes.values())
        report.graph_nodes = nodes_len
        report.graph_edges = edges_len
        
        if nodes_len > 0:
            report.average_dependency = edges_len / nodes_len
            
        if initial_count > 0:
            report.coverage_percentage = (final_count / initial_count) * 100.0
            
        # Rough token estimate (4 chars per token)
        report.estimated_tokens = total_size // 4
        
        report.processing_time_sec = time.time() - start_time
        
        if cache_total_count > 0:
            report.cache_hit_rate = (cache_hit_count / cache_total_count) * 100.0
            
        return report
