import time
import sys
import platform
from pathlib import Path
from app.domain.models.execution_result import ExecutionResult
from app.domain.models.execution_phase import ExecutionPhase

class ResultCollector:
    def collect(self, execution_id: str, task_id: str, start_time: float, 
                exit_code: int, stdout: str, stderr: str, 
                workspace_path: Path, runtime_name: str, deps: list, 
                phase: ExecutionPhase = None) -> ExecutionResult:
        end_time = time.time()
        
        # Scan files produced
        files_produced = []
        if workspace_path and workspace_path.exists():
            for p in workspace_path.rglob("*"):
                if p.is_file() and not '.packages' in p.parts:
                    files_produced.append(str(p.relative_to(workspace_path)))
                
        status = phase if phase else (ExecutionPhase.COMPLETED if exit_code == 0 else ExecutionPhase.FAILED)
        
        env_metadata = {
            "os": platform.system(),
            "python_version": sys.version,
            "platform": platform.platform()
        }
                
        return ExecutionResult(
            execution_id=execution_id,
            task_id=task_id,
            start_time=start_time,
            end_time=end_time,
            duration=end_time - start_time,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            files_produced=files_produced,
            runtime=runtime_name,
            dependencies_installed=deps,
            environment_metadata=env_metadata,
            status=status,
            python_version=sys.version,
            os_name=platform.system(),
            platform_info=platform.platform(),
            installed_package_versions=None # This could be populated by querying pip, but keeping it None for now unless pip freeze is passed.
        )
