from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from datetime import datetime
import uuid

class WorkflowState(Enum):
    PENDING = auto()
    RUNNING = auto()
    PAUSED = auto()
    FAILED = auto()
    COMPLETED = auto()
    CANCELLED = auto()

@dataclass
class WorkflowStep:
    step_id: str
    agent_identifier: str
    dependencies: List[str] = field(default_factory=list)
    status: WorkflowState = WorkflowState.PENDING
    max_retries: int = 3
    current_retries: int = 0
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # In a real system, we might hold a reference to the agent instance or a registry key.
    # We will use an abstract callable hook for the demo to decouple it.
    executor: Optional[Callable] = None 

@dataclass
class WorkflowExecution:
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    steps: Dict[str, WorkflowStep] = field(default_factory=dict)
    global_status: WorkflowState = WorkflowState.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def get_progress(self) -> dict:
        total = len(self.steps)
        completed = sum(1 for s in self.steps.values() if s.status == WorkflowState.COMPLETED)
        return {
            "execution_id": self.execution_id,
            "status": self.global_status.name,
            "total_steps": total,
            "completed_steps": completed,
            "progress_percent": (completed / total * 100) if total > 0 else 0
        }
