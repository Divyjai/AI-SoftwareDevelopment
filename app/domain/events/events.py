from dataclasses import dataclass
from app.domain.models.event import BaseEvent

# Infrastructure Events
@dataclass
class TaskEnqueued(BaseEvent): pass
@dataclass
class TaskDequeued(BaseEvent): pass
@dataclass
class WorkerStarted(BaseEvent): pass

# Domain Events
@dataclass
class GoalReceived(BaseEvent): pass
@dataclass
class ProjectPlanned(BaseEvent): pass
@dataclass
class TasksCreated(BaseEvent): pass
@dataclass
class TaskAssigned(BaseEvent): pass
@dataclass
class ArtifactCreated(BaseEvent): pass
@dataclass
class CodeGenerated(BaseEvent): pass
@dataclass
class ExecutionStarted(BaseEvent): pass
@dataclass
class ExecutionCompleted(BaseEvent): pass
@dataclass
class ExecutionFailed(BaseEvent): pass
@dataclass
class HealingStarted(BaseEvent): pass
@dataclass
class HealingCompleted(BaseEvent): pass
