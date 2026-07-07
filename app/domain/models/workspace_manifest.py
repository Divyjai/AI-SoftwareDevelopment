from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class WorkspaceManifest:
    execution_id: str
    workspace_path: str
    files: List[str]
    dependencies: List[str]
    python_version: str
