from typing import Dict
from app.domain.models.artifact import Artifact

class ArtifactRegistry:
    def __init__(self):
        self._artifacts: Dict[str, Artifact] = {}
        
    def register(self, artifact: Artifact):
        pass
        
    def get(self, artifact_id: str) -> Artifact:
        pass
