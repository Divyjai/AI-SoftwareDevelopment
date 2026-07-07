from abc import ABC, abstractmethod
import os
import subprocess
import time
from pathlib import Path
from typing import Tuple
from app.domain.models.security_policy import SecurityPolicy

class RuntimeProvider(ABC):
    @abstractmethod
    def execute(self, workspace_path: Path, command: list, policy: SecurityPolicy) -> Tuple[int, str, str]:
        pass

class SubprocessRuntime(RuntimeProvider):
    def execute(self, workspace_path: Path, command: list, policy: SecurityPolicy) -> Tuple[int, str, str]:
        env = dict(os.environ)
        
        # Enforce blocked env vars
        for var in policy.blocked_env_vars:
            if var in env:
                del env[var]
                
        # Add local packages to PYTHONPATH if using --target
        pkg_path = workspace_path / ".packages"
        if pkg_path.exists():
            env["PYTHONPATH"] = str(pkg_path) + (os.pathsep + env.get("PYTHONPATH", "") if "PYTHONPATH" in env else "")
            
        try:
            result = subprocess.run(
                command, 
                cwd=str(workspace_path), 
                capture_output=True, 
                text=True, 
                timeout=policy.max_execution_time_seconds,
                env=env
            )
            # Enforce max output size
            stdout = result.stdout[:policy.max_output_size_bytes]
            stderr = result.stderr[:policy.max_output_size_bytes]
            return result.returncode, stdout, stderr
        except subprocess.TimeoutExpired as e:
            stdout = (e.stdout.decode('utf-8') if e.stdout else "")[:policy.max_output_size_bytes]
            return -1, stdout, "Execution timed out"
