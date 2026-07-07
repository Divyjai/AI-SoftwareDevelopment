from abc import ABC, abstractmethod
from app.domain.models.artifact import Artifact

class ArtifactRepository(ABC):
    @abstractmethod
    def save(self, artifact: Artifact): pass
    @abstractmethod
    def get(self, artifact_id: str) -> Artifact: pass
    
    @abstractmethod
    def get_recent_artifacts(self, limit: int = 10) -> list[Artifact]: pass
