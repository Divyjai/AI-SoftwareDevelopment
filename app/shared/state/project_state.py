from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.domain.models.goal import Goal
from app.domain.models.phase import Phase
from app.domain.models.task import Task
from app.domain.models.artifact import Artifact
from app.domain.models.event import BaseEvent

from app.domain.models.project_graph import ProjectGraph

@dataclass
class ProjectState:
    goal: Optional[Goal] = None
    current_phase: Optional[Phase] = None
    tasks: List[Task] = field(default_factory=list)
    artifacts: List[Artifact] = field(default_factory=list)
    managers: List[Any] = field(default_factory=list)
    events: List[BaseEvent] = field(default_factory=list)
    branch: str = "main"
    metrics: Dict[str, Any] = field(default_factory=dict)
    memory: Dict[str, Any] = field(default_factory=dict)
    current_context: Dict[str, Any] = field(default_factory=dict)
    graph: ProjectGraph = field(default_factory=ProjectGraph)
