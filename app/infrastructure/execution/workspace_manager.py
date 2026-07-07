import os
import tempfile
import shutil
from pathlib import Path

class WorkspaceManager:
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or tempfile.gettempdir()
        
    def create_workspace(self, execution_id: str) -> Path:
        workspace_path = Path(self.base_dir) / f"exec_{execution_id}"
        workspace_path.mkdir(parents=True, exist_ok=True)
        return workspace_path
        
    def materialize_files(self, workspace_path: Path, files: dict):
        for filename, content in files.items():
            file_path = workspace_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            
    def cleanup(self, workspace_path: Path):
        if workspace_path.exists():
            shutil.rmtree(workspace_path, ignore_errors=True)
