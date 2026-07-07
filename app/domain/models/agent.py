from abc import ABC, abstractmethod
from app.domain.models.artifact import Artifact, ArtifactState
from app.domain.events.events import ProjectPlanned, TasksCreated
import time

class BaseEvent:
    def __init__(self, event_id: str, timestamp: float):
        self.event_id = event_id
        self.timestamp = timestamp

class PLAN_CREATED(BaseEvent):
    pass

class BaseAgent(ABC):
    @abstractmethod
    def prepare(self, task): pass
    @abstractmethod
    def plan(self): pass
    @abstractmethod
    def act(self): pass
    @abstractmethod
    def validate(self): pass
    @abstractmethod
    def report(self): pass

class PlannerAgent(BaseAgent):
    def __init__(self, state_manager, compiler, llm_provider=None):
        self.state_manager = state_manager
        self.compiler = compiler
        self.llm_provider = llm_provider
        
    def prepare(self, task):
        self.compiled_prompt = self.compiler.compile("planner", "head_manager", task, self.state_manager.state)
        
    def reason(self):
        self.generated_plan = {
            "plan": "Build API", 
            "architecture": "FastAPI+PG", 
            "tasks": [{"id": "T1", "description": "Setup DB"}, {"id": "T2", "description": "Build Routes"}]
        }
        
    def act(self):
        self.project_plan = Artifact(id="art-plan-1", version="v1", owner="planner", status=ArtifactState.GENERATED, content=self.generated_plan["plan"])
        self.arch_summary = Artifact(id="art-arch-1", version="v1", owner="planner", status=ArtifactState.GENERATED, content=self.generated_plan["architecture"])
        self.task_breakdown = Artifact(id="art-tasks-1", version="v1", owner="planner", status=ArtifactState.GENERATED, content={"tasks": self.generated_plan["tasks"]})
        self.dep_graph = Artifact(id="art-deps-1", version="v1", owner="planner", status=ArtifactState.GENERATED, content="graph {}")
        
    def validate(self):
        assert self.project_plan and self.task_breakdown
        
    def report(self):
        self.state_manager.add_artifact(self.project_plan)
        self.state_manager.add_artifact(self.arch_summary)
        self.state_manager.add_artifact(self.task_breakdown)
        self.state_manager.add_artifact(self.dep_graph)
        
        event = PLAN_CREATED(event_id="evt-plan-1", timestamp=time.time())
        self.state_manager.add_event(event)
        
        return self.task_breakdown

class BackendAgent(BaseAgent):
    def prepare(self, task): pass
    def plan(self): pass
    def act(self): pass
    def validate(self): pass
    def report(self): pass
class FrontendAgent(BaseAgent):
    def prepare(self, task): pass
    def plan(self): pass
    def act(self): pass
    def validate(self): pass
    def report(self): pass
class DatabaseAgent(BaseAgent):
    def prepare(self, task): pass
    def reason(self): pass
    def act(self): pass
    def validate(self): pass
    def report(self): pass
class TestingAgent(BaseAgent):
    def prepare(self, task): pass
    def reason(self): pass
    def act(self): pass
    def validate(self): pass
    def report(self): pass
class DeploymentAgent(BaseAgent):
    def prepare(self, task): pass
    def reason(self): pass
    def act(self): pass
    def validate(self): pass
    def report(self): pass
