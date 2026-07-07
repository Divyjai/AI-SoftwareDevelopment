from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from app.domain.models.repair import FailureReport

class FailureClassification(Enum):
    APPLICATION = auto()
    TEST = auto()
    ENVIRONMENT = auto()
    DEPENDENCY = auto()
    UNKNOWN = auto()

@dataclass
class TestExecutionResult:
    passed: bool
    failed: bool
    skipped: bool
    duration: float
    coverage: float
    failure_reports: List[FailureReport] = field(default_factory=list)

@dataclass
class TestMemory:
    endpoint: str
    generated_test: str
    repair_count: int
    final_status: str
    coverage: float
