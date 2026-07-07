import sys
from pathlib import Path
sys.path.append(str(Path(r"c:\Users\divay\adk-project")))

from app.domain.models.task import Task
from app.shared.state.project_state import ProjectState
from app.shared.state.state_manager import StateManager
from app.application.prompt_engine.prompt_compiler import PromptCompiler
from app.application.task_queue.task_queue import TaskQueue
from app.application.workflows.workflow_engine import WorkflowEngine
from app.domain.models.agent import PlannerAgent

def test_step3():
    # Setup infrastructure
    state = ProjectState()
    state_manager = StateManager(state)
    compiler = PromptCompiler(r"c:\Users\divay\adk-project")
    task_queue = TaskQueue()
    workflow_engine = WorkflowEngine(task_queue)
    
    # Initialize Planner
    planner = PlannerAgent(state_manager=state_manager, compiler=compiler)
    
    # Run Planner Lifecycle
    initial_task = Task(id="G-1", description="Build a Todo API using FastAPI and PostgreSQL")
    planner.prepare(initial_task)
    planner.reason()
    planner.act()
    planner.validate()
    breakdown_artifact = planner.report()
    
    # Validate Planner Outputs (Artifacts, State, Event)
    assert len(state.artifacts) == 4, "Planner did not store 4 artifacts in state"
    assert len(state.events) == 1, "Planner did not emit event"
    assert state.events[0].__class__.__name__ == "PLAN_CREATED", "Event is not PLAN_CREATED"
    
    # Pass artifact to workflow engine
    workflow_engine.process_task_breakdown(breakdown_artifact)
    
    # Validate Task Queue
    assert len(task_queue.queue) == 2, "Workflow engine did not queue tasks"
    assert task_queue.queue[0].id == "T1"
    
    print("VALIDATION SUCCESS: Planner -> StateManager -> WorkflowEngine -> TaskQueue integration complete.")

if __name__ == "__main__":
    test_step3()
