from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.domain.models.execution_phase import ExecutionPhase

@dataclass
class ExecutionResult:
    execution_id: str
    task_id: str
    start_time: float
    end_time: float
    duration: float
    exit_code: int
    stdout: str
    stderr: str
    files_produced: List[str]
    runtime: str
    dependencies_installed: List[str]
    environment_metadata: Dict[str, Any]
    status: ExecutionPhase
    python_version: Optional[str] = None
    os_name: Optional[str] = None
    platform_info: Optional[str] = None
    installed_package_versions: Optional[Dict[str, str]] = None
    retry_count: int = 0
    retry_reason: Optional[str] = None
    previous_execution_id: Optional[str] = None
