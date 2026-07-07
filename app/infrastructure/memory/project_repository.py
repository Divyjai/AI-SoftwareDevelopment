from typing import Optional
from app.interfaces.project_repository import ProjectRepository
from app.shared.state.project_state import ProjectState

class InMemoryProjectRepository(ProjectRepository):
    def __init__(self):
        self._state: Optional[ProjectState] = None

    def get_project_state(self) -> Optional[ProjectState]:
        return self._state
        
    def save_project_state(self, state: ProjectState):
        self._state = state
