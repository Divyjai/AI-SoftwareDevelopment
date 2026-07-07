import pytest
from app.domain.models.workflow import WorkflowExecution, WorkflowStep, WorkflowState
from app.application.workflow.coordinator import WorkflowCoordinator

class MockRepairEngine:
    def __init__(self):
        self.repairs_triggered = 0

    def run_repair(self, execution_id: str, raw_failure_output: str):
        self.repairs_triggered += 1

def test_workflow_coordinator_successful_dag():
    repair_engine = MockRepairEngine()
    coordinator = WorkflowCoordinator(repair_engine)
    
    execution = WorkflowExecution()
    
    # Track execution order
    executed_order = []
    
    def make_executor(name):
        def _exec():
            executed_order.append(name)
        return _exec

    step1 = WorkflowStep(step_id="planner", agent_identifier="planner_agent", executor=make_executor("planner"))
    step2 = WorkflowStep(step_id="database", agent_identifier="db_agent", dependencies=["planner"], executor=make_executor("database"))
    step3 = WorkflowStep(step_id="backend", agent_identifier="backend_agent", dependencies=["database"], executor=make_executor("backend"))
    step4 = WorkflowStep(step_id="qa", agent_identifier="qa_agent", dependencies=["backend"], executor=make_executor("qa"))
    
    execution.steps = {
        "planner": step1,
        "database": step2,
        "backend": step3,
        "qa": step4
    }
    
    exec_id = coordinator.submit(execution)
    assert exec_id == execution.execution_id
    
    success = coordinator.execute(exec_id)
    
    assert success is True
    assert execution.global_status == WorkflowState.COMPLETED
    assert executed_order == ["planner", "database", "backend", "qa"]
    
    progress = coordinator.get_progress(exec_id)
    assert progress["progress_percent"] == 100

def test_workflow_coordinator_retry_and_repair():
    repair_engine = MockRepairEngine()
    coordinator = WorkflowCoordinator(repair_engine)
    
    execution = WorkflowExecution()
    
    # This step will fail 2 times, then succeed on the 3rd attempt.
    class FlakyExecutor:
        def __init__(self):
            self.attempts = 0
            
        def __call__(self):
            self.attempts += 1
            if self.attempts < 3:
                raise ValueError("Transient error")
                
    flaky = FlakyExecutor()
    
    step1 = WorkflowStep(step_id="flaky_step", agent_identifier="test_agent", max_retries=3, executor=flaky)
    execution.steps = {"flaky_step": step1}
    
    exec_id = coordinator.submit(execution)
    success = coordinator.execute(exec_id)
    
    assert success is True
    assert execution.global_status == WorkflowState.COMPLETED
    assert flaky.attempts == 3
    assert repair_engine.repairs_triggered == 2
    assert step1.current_retries == 2

def test_workflow_coordinator_failure_exceeds_retries():
    repair_engine = MockRepairEngine()
    coordinator = WorkflowCoordinator(repair_engine)
    
    execution = WorkflowExecution()
    
    def always_fails():
        raise ValueError("Fatal error")
                
    step1 = WorkflowStep(step_id="failing_step", agent_identifier="test_agent", max_retries=1, executor=always_fails)
    execution.steps = {"failing_step": step1}
    
    exec_id = coordinator.submit(execution)
    success = coordinator.execute(exec_id)
    
    assert success is False
    assert execution.global_status == WorkflowState.FAILED
    assert step1.current_retries == 2 # Initial + 1 retry
    assert repair_engine.repairs_triggered == 1

def test_workflow_coordinator_parallel():
    from app.application.workflow.coordinator import SchedulerMode
    import time
    repair_engine = MockRepairEngine()
    coordinator = WorkflowCoordinator(repair_engine, scheduler_mode=SchedulerMode.PARALLEL)
    
    execution = WorkflowExecution()
    
    # We will track execution concurrency
    started = []
    
    def make_executor(name):
        def _exec():
            started.append(name)
            time.sleep(0.1)  # Simulate work
        return _exec

    # Independent steps
    step1 = WorkflowStep(step_id="task_A", agent_identifier="agent_a", executor=make_executor("task_A"))
    step2 = WorkflowStep(step_id="task_B", agent_identifier="agent_b", executor=make_executor("task_B"))
    
    execution.steps = {
        "task_A": step1,
        "task_B": step2,
    }
    
    exec_id = coordinator.submit(execution)
    
    start_time = time.time()
    success = coordinator.execute(exec_id)
    end_time = time.time()
    
    assert success is True
    assert execution.global_status == WorkflowState.COMPLETED
    assert "task_A" in started
    assert "task_B" in started
    
    # Both should finish roughly in 0.1s rather than 0.2s if they ran in parallel
    assert (end_time - start_time) < 0.18
