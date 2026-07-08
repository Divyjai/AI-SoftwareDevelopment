from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Any

class FrontendNodeType(Enum):
    PAGE = auto()
    LAYOUT = auto()
    COMPONENT = auto()
    HOOK = auto()
    SERVICE = auto()
    STYLE = auto()
    ROUTE = auto()
    FORM = auto()
    STATE = auto()
    API_CLIENT = auto()
    THEME = auto()
    ICON = auto()
    ASSET = auto()
    MIDDLEWARE = auto()
    PROVIDER = auto()
    CONTEXT = auto()

class FrontendEdgeType(Enum):
    USES = auto()
    IMPORTS = auto()
    CALLS = auto()
    CONTAINS = auto()
    NAVIGATES_TO = auto()
    FETCHES = auto()
    DEPENDS_ON = auto()
    WRAPS = auto()
    PROVIDES = auto()
    CONSUMES = auto()
    STYLES = auto()
    AUTHENTICATES = auto()

@dataclass
class FrontendGraphVersion:
    version: str
    parent_version: str
    created_at: float
    execution_id: str
    checksum: str

@dataclass
class FrontendGraphNode:
    id: str
    type: FrontendNodeType
    name: str
    file_path: str
    backend_reference_id: str = None  # Link to ProjectGraph backend node
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FrontendGraphEdge:
    source_id: str
    target_id: str
    type: FrontendEdgeType
    metadata: Dict[str, Any] = field(default_factory=dict)

class FrontendGraph:
    def __init__(self):
        self.nodes: Dict[str, FrontendGraphNode] = {}
        self.edges: List[FrontendGraphEdge] = []
        
        self._adj_out: Dict[str, List[FrontendGraphEdge]] = {}
        self._adj_in: Dict[str, List[FrontendGraphEdge]] = {}

    def add_node(self, node: FrontendGraphNode):
        self.nodes[node.id] = node
        if node.id not in self._adj_out:
            self._adj_out[node.id] = []
        if node.id not in self._adj_in:
            self._adj_in[node.id] = []

    def add_edge(self, edge: FrontendGraphEdge):
        if edge.source_id not in self.nodes or edge.target_id not in self.nodes:
            raise ValueError(f"Nodes must exist in graph before adding edge. Missing: {edge.source_id} or {edge.target_id}")
            
        self.edges.append(edge)
        self._adj_out[edge.source_id].append(edge)
        self._adj_in[edge.target_id].append(edge)

    def get_node(self, node_id: str) -> FrontendGraphNode:
        return self.nodes.get(node_id)
