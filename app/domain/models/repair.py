from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class FailureReport:
    failure_type: str  # SyntaxError, ModuleNotFoundError, PytestFailure, etc.
    root_cause: str
    severity: str
    affected_files: List[str]
    affected_nodes: List[str]
    stack_trace: str
    suggested_strategy: str
    confidence: float
    is_deterministic: bool = False

@dataclass
class RepairPlan:
    files_to_modify: List[str]
    functions_to_modify: List[str]
    dependencies: List[str]
    repair_reason: str
    previous_similar_repairs: List[str]
    execution_constraints: List[str]

@dataclass
class Patch:
    file: str
    target_node: str
    node_type: str
    change_type: str  # REPLACE, ADD, DELETE
    old_fragment: str
    new_fragment: str
    reason: str
    confidence: float

@dataclass
class RepairSession:
    repair_id: str
    execution_id: str
    failure_report: FailureReport
    repair_plan: Optional[RepairPlan] = None
    patches: List[Patch] = field(default_factory=list)
    attempt_number: int = 1
    status: str = "IN_PROGRESS"  # IN_PROGRESS, SUCCESS, FAILED
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

@dataclass
class RetryPolicy:
    failure_type_config: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "SyntaxError": {"attempts": 2, "backoff": 0, "escalation": "abort"},
        "ModuleNotFoundError": {"attempts": 1, "backoff": 0, "escalation": "abort"},
        "PytestFailure": {"attempts": 3, "backoff": 0, "escalation": "abort"}
    })
    
    def get_max_attempts(self, failure_type: str) -> int:
        for key in self.failure_type_config:
            if key in failure_type:
                return self.failure_type_config[key].get("attempts", 1)
        return 1  # Default fallback
