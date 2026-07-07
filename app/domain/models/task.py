from dataclasses import dataclass, field
from typing import List
from enum import Enum

class TaskState(Enum):
    CREATED = "created"
    PLANNED = "planned"
    ASSIGNED = "assigned"
    PREPARING = "preparing"
    REASONING = "reasoning"
    EXECUTING = "executing"
    VALIDATING = "validating"
    REVIEW = "review"
    APPROVED = "approved"
    COMPLETED = "completed"
    ARCHIVED = "archived"

@dataclass
class Task:
    id: str
    description: str
    status: TaskState = TaskState.CREATED
    dependencies: List[str] = field(default_factory=list)
