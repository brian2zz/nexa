from typing import Dict, List
from .models import KnowledgeNode, KnowledgeEdge

class DependencyGraph:
    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}

    def add_node(self, path: str):
        if path not in self.nodes:
            self.nodes[path] = KnowledgeNode(path=path)

    def add_edge(self, source: str, target: str, relation_type: str = "IMPORTS"):
        self.add_node(source)
        self.add_node(target)
        edge = KnowledgeEdge(source=source, target=target, relation_type=relation_type)
        self.nodes[source].dependencies.append(edge)

    def get_node(self, path: str) -> KnowledgeNode:
        return self.nodes.get(path)

    def get_all_nodes(self) -> List[str]:
        return list(self.nodes.keys())
