from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.domain.models.task import Task
from app.domain.memory.models import MemoryRecord
from app.domain.models.artifact import Artifact
from app.shared.state.project_state import ProjectState

@dataclass
class RetrievalMetadata:
    memory_count: int
    artifact_count: int
    execution_count: int
    average_similarity: float
    retrieval_duration: float
    strategy: str

from app.domain.models.project_graph import ProjectGraph, GraphNode

@dataclass
class KnowledgeBundle:
    goal: str
    workflow: str
    project: str
    current_task: Task
    project_summary: str
    relevant_memories: List[MemoryRecord] = field(default_factory=list)
    artifacts: List[Artifact] = field(default_factory=list)
    execution_history: List[Dict[str, Any]] = field(default_factory=list)
    similar_failures: List[MemoryRecord] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    agent_settings: Dict[str, Any] = field(default_factory=dict)
    system_context: str = ""
    retrieval_metadata: Optional[RetrievalMetadata] = None
    project_graph: Optional[ProjectGraph] = None
    relevant_nodes: List[GraphNode] = field(default_factory=list)
