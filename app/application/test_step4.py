import sys
from pathlib import Path
sys.path.append(str(Path(r"c:\Users\divay\adk-project")))

from app.domain.models.task import Task
from app.shared.state.project_state import ProjectState
from app.application.prompt_engine.prompt_compiler import PromptCompiler
from app.domain.models.agent_context import AgentContext
from app.application.agents.backend_agent import BackendAgent
from app.domain.models.artifact import Artifact
from app.application.task_queue.task_queue import TaskQueue
from app.application.task_queue.task_factory import TaskFactory
from app.application.task_queue.task_assignment import TaskAssignmentPolicy
from app.application.task_queue.task_dispatcher import TaskDispatcher

class MockRepo:
    def __init__(self): self.saved = []
    def save(self, art): self.saved.append(art)
    def get(self, id): return None
class MockBus:
    def __init__(self): self.events = []
    def publish(self, evt): self.events.append(evt)
class MockExec:
    def __init__(self): self.executed = []
    def execute(self, art, ctx): self.executed.append(art.id)

def test_full_loop():
    # Setup Infrastructure
    factory = TaskFactory()
    queue = TaskQueue()
    policy = TaskAssignmentPolicy()
    
    # 1. Workflow orchestrates task creation
    task = factory.create("T-100", "Build Todo API endpoints")
    queue.enqueue(task)
    
    # Setup Context
    repo = MockRepo()
    bus = MockBus()
    exec_engine = MockExec()
    state = ProjectState()
    compiler = PromptCompiler(r"c:\Users\divay\adk-project")
    
    def context_factory(t):
        return AgentContext(
            task=t, project_state=state, repository=repo, event_bus=bus,
            compiler=compiler, execution_engine=exec_engine, knowledge_service=None, settings={},
            llm=None, correlation_id="corr-123"
        )
    
    # Setup Agent Registry & Dispatcher
    backend = BackendAgent()
    dispatcher = TaskDispatcher(queue, policy, {"BackendAgent": backend})
    
    agent_name = policy.assign(task)
    print(f"Task desc: {task.description}, assigned to: {agent_name}")
    print(f"Agents registry keys: {list(dispatcher.agents.keys())}")
    dispatched = dispatcher.dispatch_next(context_factory)
    assert dispatched, "Dispatcher failed to route task"
    assert len(repo.saved) == 1, "Backend did not save artifact to repository"
    assert len(state.artifacts) == 1, "Backend did not update project state"
    assert len(bus.events) == 1, "Backend did not emit CodeGenerated event"
    assert bus.events[0].__class__.__name__ == "CodeGenerated", "Incorrect event emitted"
    assert len(exec_engine.executed) == 1, "Backend did not hand off to Execution Engine"
    
    print("VALIDATION SUCCESS: Dispatcher -> Backend -> Repository -> EventBus -> ExecutionEngine loop complete.")

if __name__ == "__main__":
    test_full_loop()
