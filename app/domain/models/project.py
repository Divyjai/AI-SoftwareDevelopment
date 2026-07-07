from dataclasses import dataclass, field
from typing import List
from app.domain.models.goal import Goal
from app.domain.models.phase import Phase
from app.domain.models.task import Task
from app.domain.models.artifact import Artifact
from app.domain.models.event import BaseEvent

@dataclass
class Project:
    id: str
    name: str
    goals: List[Goal] = field(default_factory=list)
    phases: List[Phase] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    artifacts: List[Artifact] = field(default_factory=list)
    events: List[BaseEvent] = field(default_factory=list)
