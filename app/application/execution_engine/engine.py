import time
import uuid
import sys
from typing import Dict
from app.infrastructure.execution.workspace_manager import WorkspaceManager
from app.infrastructure.execution.dependency_manager import DependencyManager
from app.infrastructure.execution.runtime_provider import RuntimeProvider
from app.infrastructure.execution.result_collector import ResultCollector
from app.domain.models.execution_result import ExecutionResult
from app.domain.models.workspace_manifest import WorkspaceManifest
from app.domain.models.security_policy import SecurityPolicy
from app.domain.models.execution_phase import ExecutionPhase

class ExecutionEngine:
    def __init__(self, workspace_manager: WorkspaceManager, dep_manager: DependencyManager,
                 runtime: RuntimeProvider, collector: ResultCollector):
        self.workspace_manager = workspace_manager
        self.dep_manager = dep_manager
        self.runtime = runtime
        self.collector = collector
        
    def execute(self, task_id: str, files: Dict[str, str], command: list) -> ExecutionResult:
        execution_id = str(uuid.uuid4())
        workspace_path = None
        start_time = time.time()
        current_phase = ExecutionPhase.PREPARING_WORKSPACE
        
        try:
            # 1. Create Workspace & Materialize
            workspace_path = self.workspace_manager.create_workspace(execution_id)
            self.workspace_manager.materialize_files(workspace_path, files)
            
            # 2. Extract dependencies
            deps = []
            if "requirements.txt" in files:
                deps = files["requirements.txt"].split("\n")
            
            # 3. Generate and Persist Manifest
            manifest = WorkspaceManifest(
                execution_id=execution_id,
                workspace_path=str(workspace_path),
                files=list(files.keys()),
                dependencies=deps,
                python_version=sys.version
            )
            # (In a real system, we'd save this manifest to a DB or log here)
            
            # 4. Install Dependencies
            current_phase = ExecutionPhase.INSTALLING_DEPENDENCIES
            installed_deps = self.dep_manager.install_dependencies(workspace_path)
            
            # 5. Execute with Policy
            current_phase = ExecutionPhase.EXECUTING
            policy = SecurityPolicy()
            exit_code, stdout, stderr = self.runtime.execute(workspace_path, command, policy)
            
            # 6. Collect Results
            current_phase = ExecutionPhase.COLLECTING_RESULTS
            return self.collector.collect(
                execution_id, task_id, start_time, exit_code, stdout, stderr,
                workspace_path, self.runtime.__class__.__name__, installed_deps,
                phase=ExecutionPhase.COMPLETED if exit_code == 0 else ExecutionPhase.FAILED
            )
        except Exception as e:
            # Handle catastrophic failure in setup
            return self.collector.collect(
                execution_id, task_id, start_time, -2, "", str(e),
                workspace_path, self.runtime.__class__.__name__, [],
                phase=current_phase
            )
        finally:
            if workspace_path:
                self.workspace_manager.cleanup(workspace_path)
