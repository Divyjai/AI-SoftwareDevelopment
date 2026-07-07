from app.shared.state.project_state import ProjectState
from app.domain.models.artifact import Artifact
from app.domain.models.event import BaseEvent

class StateManager:
    def __init__(self, project_state: ProjectState):
        self.state = project_state
        
    def update_task(self, task_id: str, status):
        for t in self.state.tasks:
            if t.id == task_id:
                t.status = status
                break
        
    def update_phase(self, phase):
        self.state.current_phase = phase
        
    def add_artifact(self, artifact: Artifact):
        self.state.artifacts.append(artifact)
        
    def add_event(self, event: BaseEvent):
        self.state.events.append(event)
        
    def update_metrics(self, metrics: dict):
        self.state.metrics.update(metrics)
        
    def update_branch(self, branch_name: str):
        self.state.branch = branch_name
