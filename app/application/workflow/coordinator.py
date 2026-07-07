from app.domain.models.workflow import WorkflowExecution, WorkflowStep, WorkflowState
from typing import Dict, List
from datetime import datetime
from enum import Enum
import concurrent.futures

class SchedulerMode(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"

class WorkflowCoordinator:
    def __init__(self, repair_engine, scheduler_mode: SchedulerMode = SchedulerMode.SEQUENTIAL):
        self.repair_engine = repair_engine
        self.scheduler_mode = scheduler_mode
        self.active_executions: Dict[str, WorkflowExecution] = {}

    def submit(self, execution: WorkflowExecution) -> str:
        self.active_executions[execution.execution_id] = execution
        return execution.execution_id

    def execute(self, execution_id: str) -> bool:
        execution = self.active_executions.get(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found.")

        execution.global_status = WorkflowState.RUNNING
        execution.started_at = datetime.utcnow()

        while True:
            if execution.global_status == WorkflowState.CANCELLED:
                break
                
            runnable_steps = self._get_runnable_steps(execution)
            
            if not runnable_steps:
                if all(s.status == WorkflowState.COMPLETED for s in execution.steps.values()):
                    execution.global_status = WorkflowState.COMPLETED
                elif any(s.status == WorkflowState.FAILED for s in execution.steps.values()):
                    execution.global_status = WorkflowState.FAILED
                else:
                    execution.global_status = WorkflowState.FAILED
                break

            if self.scheduler_mode == SchedulerMode.PARALLEL and len(runnable_steps) > 1:
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    futures = {pool.submit(self._execute_step, step, execution): step for step in runnable_steps}
                    for future in concurrent.futures.as_completed(futures):
                        success = future.result()
                        if not success:
                            execution.global_status = WorkflowState.FAILED
            else:
                for step in runnable_steps:
                    success = self._execute_step(step, execution)
                    if not success:
                        execution.global_status = WorkflowState.FAILED
                        break
                    
            if execution.global_status == WorkflowState.FAILED:
                break

        execution.completed_at = datetime.utcnow()
        return execution.global_status == WorkflowState.COMPLETED

    def _get_runnable_steps(self, execution: WorkflowExecution) -> List[WorkflowStep]:
        runnable = []
        for step in execution.steps.values():
            if step.status == WorkflowState.PENDING:
                # Check dependencies
                deps_met = all(
                    execution.steps[dep].status == WorkflowState.COMPLETED 
                    for dep in step.dependencies
                )
                if deps_met:
                    runnable.append(step)
        return runnable

    def _execute_step(self, step: WorkflowStep, execution: WorkflowExecution) -> bool:
        step.status = WorkflowState.RUNNING
        step.started_at = datetime.utcnow()

        while step.current_retries <= step.max_retries:
            try:
                if execution.global_status == WorkflowState.CANCELLED:
                    step.status = WorkflowState.CANCELLED
                    return False
                    
                if step.executor:
                    step.executor()
                    
                step.status = WorkflowState.COMPLETED
                step.completed_at = datetime.utcnow()
                return True
            except Exception as e:
                step.current_retries += 1
                step.error_message = str(e)
                
                if step.current_retries <= step.max_retries:
                    # Trigger Repair Engine
                    if self.repair_engine:
                        self.repair_engine.run_repair(
                            execution_id=step.step_id,
                            raw_failure_output=str(e)
                        )
                else:
                    step.status = WorkflowState.FAILED
                    step.completed_at = datetime.utcnow()
                    return False
                    
        return False

    def cancel(self, execution_id: str):
        execution = self.active_executions.get(execution_id)
        if execution and execution.global_status == WorkflowState.RUNNING:
            execution.global_status = WorkflowState.CANCELLED

    def get_progress(self, execution_id: str) -> dict:
        execution = self.active_executions.get(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found.")
        return execution.get_progress()
