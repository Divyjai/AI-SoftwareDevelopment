from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Any, Set

class NodeType(Enum):
    FILE = auto()
    CLASS = auto()
    FUNCTION = auto()
    DEPENDENCY = auto()
    IMPORT = auto()
    TEST = auto()
    ENDPOINT = auto()
    MODULE = auto()
    DATABASE = auto()
    TABLE = auto()
    COLUMN = auto()
    INDEX = auto()
    CONSTRAINT = auto()
    VIEW = auto()
    TRIGGER = auto()
    MIGRATION = auto()
    ORM_MODEL = auto()

class EdgeType(Enum):
    CONTAINS = auto()
    IMPORTS = auto()
    CALLS = auto()
    TESTS = auto()
    DEPENDS_ON = auto()
    IMPLEMENTS = auto()
    HANDLES = auto()
    REFERENCES = auto()
    INDEXES = auto()
    MIGRATES_TO = auto()
    GENERATES = auto()
    MAPS_TO = auto()
    USES = auto()

class CoverageStatus(Enum):
    UNCOVERED = auto()
    PARTIAL = auto()
    COVERED = auto()

@dataclass
class CoverageMetrics:
    line_coverage: float = 0.0
    branch_coverage: float = 0.0
    endpoint_coverage: float = 0.0
    function_coverage: float = 0.0
    module_coverage: float = 0.0

@dataclass
class RiskMetrics:
    complexity: float = 1.0
    change_frequency: int = 0
    repair_frequency: int = 0
    
    @property
    def risk_score(self) -> float:
        # Simple heuristic: high complexity + high churn + high repairs = high risk
        return self.complexity * (1.0 + self.change_frequency * 0.5 + self.repair_frequency * 2.0)

@dataclass
class GraphNode:
    id: str
    type: NodeType
    name: str
    file_path: str
    coverage_status: CoverageStatus = CoverageStatus.UNCOVERED
    risk_metrics: RiskMetrics = field(default_factory=RiskMetrics)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GraphEdge:
    source_id: str
    target_id: str
    type: EdgeType
    metadata: Dict[str, Any] = field(default_factory=dict)

class ProjectGraph:
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.coverage_metrics: CoverageMetrics = CoverageMetrics()
        
        # Adjacency list for fast traversal
        self._adj_out: Dict[str, List[GraphEdge]] = {}
        self._adj_in: Dict[str, List[GraphEdge]] = {}

    def add_node(self, node: GraphNode):
        self.nodes[node.id] = node
        if node.id not in self._adj_out:
            self._adj_out[node.id] = []
        if node.id not in self._adj_in:
            self._adj_in[node.id] = []

    def add_edge(self, edge: GraphEdge):
        if edge.source_id not in self.nodes or edge.target_id not in self.nodes:
            raise ValueError(f"Nodes must exist in graph before adding edge. Missing: {edge.source_id} or {edge.target_id}")
            
        self.edges.append(edge)
        self._adj_out[edge.source_id].append(edge)
        self._adj_in[edge.target_id].append(edge)

    def get_node(self, node_id: str) -> GraphNode:
        return self.nodes.get(node_id)

    def get_blast_radius(self, node_id: str, depth: int = 1) -> List[GraphNode]:
        """
        Find all nodes that could be affected if the given node_id changes.
        This usually means finding nodes that depend on or call this node.
        (Traversing INCOMING edges like IMPORTS, CALLS, DEPENDS_ON)
        """
        if node_id not in self.nodes:
            return []
            
        visited = set()
        queue = [(node_id, 0)]
        affected_nodes = []
        
        while queue:
            current_id, current_depth = queue.pop(0)
            
            if current_id in visited:
                continue
            visited.add(current_id)
            
            # Don't add the root node itself
            if current_id != node_id:
                affected_nodes.append(self.nodes[current_id])
                
            if current_depth >= depth:
                continue
                
            # If current_id changes, who relies on it?
            # E.g., someone IMPORTS it (edge: other -> IMPORTS -> current_id)
            # So we look at incoming edges.
            for edge in self._adj_in.get(current_id, []):
                # We mainly care about IMPORTS, CALLS, DEPENDS_ON
                if edge.type in [EdgeType.IMPORTS, EdgeType.CALLS, EdgeType.DEPENDS_ON, EdgeType.TESTS]:
                    queue.append((edge.source_id, current_depth + 1))
                    
        return affected_nodes

    def get_dependencies(self, node_id: str, depth: int = 1) -> List[GraphNode]:
        """
        Find all nodes that the given node_id relies on.
        (Traversing OUTGOING edges like IMPORTS, CALLS, DEPENDS_ON)
        """
        if node_id not in self.nodes:
            return []
            
        visited = set()
        queue = [(node_id, 0)]
        dependency_nodes = []
        
        while queue:
            current_id, current_depth = queue.pop(0)
            
            if current_id in visited:
                continue
            visited.add(current_id)
            
            if current_id != node_id:
                dependency_nodes.append(self.nodes[current_id])
                
            if current_depth >= depth:
                continue
                
            for edge in self._adj_out.get(current_id, []):
                if edge.type in [EdgeType.IMPORTS, EdgeType.CALLS, EdgeType.DEPENDS_ON]:
                    queue.append((edge.target_id, current_depth + 1))
                    
        return dependency_nodes
