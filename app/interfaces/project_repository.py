from abc import ABC, abstractmethod
from typing import Optional
from app.shared.state.project_state import ProjectState

class ProjectRepository(ABC):
    @abstractmethod
    def get_project_state(self) -> Optional[ProjectState]:
        pass
    
    @abstractmethod
    def save_project_state(self, state: ProjectState):
        pass
