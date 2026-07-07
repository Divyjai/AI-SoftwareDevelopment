from abc import ABC, abstractmethod
from app.domain.models.artifact import Artifact

class ExecutionEngine(ABC):
    @abstractmethod
    def execute(self, artifact: Artifact, context) -> str: pass
