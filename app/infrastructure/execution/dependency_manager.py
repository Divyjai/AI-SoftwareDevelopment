import subprocess
from pathlib import Path
from typing import List

class DependencyManager:
    def install_dependencies(self, workspace_path: Path) -> List[str]:
        installed = []
        req_file = workspace_path / "requirements.txt"
        if req_file.exists():
            try:
                subprocess.run(["pip", "install", "-r", str(req_file), "--target", str(workspace_path / ".packages")], 
                               cwd=str(workspace_path), check=True, capture_output=True)
                installed.append("requirements.txt")
            except subprocess.CalledProcessError as e:
                raise Exception(f"Failed to install dependencies: {e.stderr.decode('utf-8')}")
        return installed
