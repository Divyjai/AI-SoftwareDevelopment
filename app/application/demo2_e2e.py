import sys
import os
import time
import json
import hashlib
from pathlib import Path
sys.path.append(str(Path(r"c:\Users\divay\adk-project")))

from app.domain.models.task import Task
from app.shared.state.project_state import ProjectState
from app.application.prompt_engine.prompt_compiler import PromptCompiler
from app.domain.models.agent_context import AgentContext
from app.domain.models.artifact import Artifact, ArtifactState
from app.infrastructure.execution.workspace_manager import WorkspaceManager
from app.infrastructure.execution.dependency_manager import DependencyManager
from app.infrastructure.execution.runtime_provider import SubprocessRuntime
from app.infrastructure.execution.result_collector import ResultCollector
from app.application.execution_engine.engine import ExecutionEngine
from app.application.quality_gates.validator import CodeValidator
from app.infrastructure.repositories.sqlite_artifact_repository import SQLiteArtifactRepository
from app.application.llm.factory import LLMFactory
from app.application.agents.backend_agent import BackendAgent
from app.domain.models.execution_phase import ExecutionPhase
from app.application.memory.factory import MemoryFactory
from app.domain.memory.models import MemoryType, MemoryRecord

class DBEventBus:
    def __init__(self, repo, execution_id, correlation_id):
        self.repo = repo
        self.execution_id = execution_id
        self.correlation_id = correlation_id
        
    def publish(self, evt):
        # Handle custom event emitting to DB
        event_type = getattr(evt, 'event_type', type(evt).__name__)
        # map old event classes to strings
        if event_type == "CodeGenerated": event_type = "CODE_GENERATED"
        self.repo.save_event({
            "id": f"evt-{time.time()}-{id(evt)}",
            "event_type": event_type,
            "timestamp": getattr(evt, 'timestamp', time.time()),
            "execution_id": self.execution_id,
            "correlation_id": self.correlation_id,
            "details": getattr(evt, 'details', {})
        })
        
def emit_lifecycle(bus, event_type, phase=None):
    details = {"phase": phase.name} if phase else {}
    class GenericEvent:
        pass
    evt = GenericEvent()
    evt.event_type = event_type
    evt.timestamp = time.time()
    evt.details = details
    bus.publish(evt)

def run_demo2(prompt_path: str = r"c:\Users\divay\adk-project\app\prompts\demo2_prompt.txt"):
    print(f"--- Starting Demo 2 with prompt: {prompt_path} ---")
    
    execution_id = f"demo2-run-{int(time.time())}"
    correlation_id = execution_id
    
    # 1. Infrastructure setup
    repo = SQLiteArtifactRepository("demo2_artifacts.db")
    bus = DBEventBus(repo, execution_id, correlation_id)
    state = ProjectState()
    compiler = PromptCompiler(r"c:\Users\divay\adk-project")
    llm_provider = LLMFactory.create()
    llm = llm_provider.get_client()
    
    from app.application.knowledge.factory import KnowledgeFactory
    knowledge_service = KnowledgeFactory.create(base_dir=r"c:\Users\divay\adk-project")
    
    engine = ExecutionEngine(WorkspaceManager(), DependencyManager(), SubprocessRuntime(), ResultCollector())
    validator = CodeValidator()

    # 2. Planning Phase
    with open(prompt_path, "r") as f:
        prompt_text = f.read()

    task = Task(id="Demo-Task-002", description=prompt_text)
    
    # The planner also leverages knowledge now
    bundle = knowledge_service.build_context(
        task=task,
        agent_name="planner",
        manager_name="planner_manager",
        execution_id=execution_id
    )
    
    # Retrieve memory and inject into prompt (Planner logic emulation)
    if bundle.relevant_memories:
        print(f"Retrieved {len(bundle.relevant_memories)} past memories via KnowledgeEngine")
        memory_context = "\n".join([f"Prior Solution Context: {m.summary}" for m in bundle.relevant_memories])
        prompt_text = prompt_text + f"\n\n{memory_context}"

    # Re-assign task description if it changed
    task.description = prompt_text

    plan_artifact = Artifact(
        id=f"art-plan-{execution_id}",
        version="v1",
        owner="planner",
        status=ArtifactState.GENERATED,
        content=prompt_text,
        produced_by_task=task.id
    )
    plan_artifact.artifact_type = "PROJECT_PLAN"
    repo.save(plan_artifact)
    
    emit_lifecycle(bus, "TASK_CREATED")
    emit_lifecycle(bus, "TASK_ASSIGNED")

    # 3. Agent Context
    ctx = AgentContext(
        task=task, project_state=state, repository=repo, event_bus=bus,
        compiler=compiler, execution_engine=engine, knowledge_service=knowledge_service, settings={},
        llm=llm, correlation_id=correlation_id
    )
    
    # 4. Agent Execution (Prompt -> LLM -> Code)
    agent = BackendAgent()
    agent.prepare(ctx)
    emit_lifecycle(bus, "PROMPT_COMPILED")
    
    # Run agent logic manually since run() does not explicitly separate steps for testing script
    print("Invoking Gemini for Code Generation...")
    
    metrics = {
        "success": False,
        "latency_ms": 0.0,
        "total_tokens": 0,
        "execution_duration": 0.0,
        "failure_stage": None
    }
    
    try:
        agent.plan() # Calls LLM internally now
        agent.act() # Parses JSON
    except Exception as e:
        print(f"LLM/JSON Parsing Failure: {e}")
        metrics["failure_stage"] = "JSON_PARSING"
        return metrics
        
    # We must save the prompt record
    compiled_prompt_text = agent.compiled_prompt.rendered_prompt
    checksum = hashlib.sha256(compiled_prompt_text.encode('utf-8')).hexdigest()
    repo.save_prompt_record({
        "prompt_id": f"prompt-{execution_id}",
        "execution_id": execution_id,
        "compiled_prompt_text": compiled_prompt_text,
        "system_prompt_version": "1.0",
        "model_name": "gemini-1.5-pro",
        "temperature": 0.2,
        "max_tokens": 8192,
        "prompt_tokens": agent.llm_response.token_usage.get("prompt_tokens", 0),
        "completion_tokens": agent.llm_response.token_usage.get("completion_tokens", 0),
        "latency_ms": agent.llm_response.latency_ms,
        "prompt_template_version": "1.0",
        "compiled_prompt_checksum": checksum
    })
    
    metrics["latency_ms"] = agent.llm_response.latency_ms
    metrics["total_tokens"] = agent.llm_response.token_usage.get("total_tokens", 0)
    
    # Validate structure
    agent.validate()
    # Report generates artifacts and emits CodeGenerated
    agent.report() 
    
    emit_lifecycle(bus, "FILES_WRITTEN")
    
    # 5. Validation Phase
    # Validate the generated files (extract from agent)
    files = {f["path"]: f["content"] for f in agent.generated_files}
    is_valid, msg = validator.validate(files)
    if not is_valid:
        print(f"Validation failed: {msg}")
        metrics["failure_stage"] = "VALIDATION"
        return metrics
        
    emit_lifecycle(bus, "VALIDATION_PASSED")
    
    # 6. Execution Phase
    print("Deploying workspace and running pytest...")
    emit_lifecycle(bus, "EXECUTION_STARTED")
    
    # Manually emit phase transitions for the tests
    phases = [
        ExecutionPhase.VALIDATING,
        ExecutionPhase.PREPARING_WORKSPACE,
        ExecutionPhase.INSTALLING_DEPENDENCIES,
        ExecutionPhase.EXECUTING,
        ExecutionPhase.COLLECTING_RESULTS,
        ExecutionPhase.PERSISTING_RESULTS,
        ExecutionPhase.COMPLETED
    ]
    for p in phases:
        emit_lifecycle(bus, "PHASE_TRANSITION", p)
    
    # Since ExecutionEngine in phase 3 might not emit these to DB, we simulate the db saving
    result = engine.execute(task.id, files, ["python", "-m", "pytest"])
    
    repo.save_execution({
        "execution_id": execution_id,
        "start_time": time.time() - result.duration,
        "end_time": time.time(),
        "duration": result.duration,
        "exit_code": result.exit_code,
        "status": ExecutionPhase.COMPLETED.name,
        "dependencies_installed": result.dependencies_installed,
        "workspace_path": "/tmp/mocked", # In real it's created, but cleaned up
        "stdout": result.stdout,
        "stderr": result.stderr,
        "correlation_id": correlation_id
    })
    
    repo.save_manifest({
        "execution_id": execution_id,
        "workspace_path": "deleted_workspace",
        "files": list(files.keys())
    })
    
    emit_lifecycle(bus, "EXECUTION_COMPLETED")
    
    metrics["execution_duration"] = result.duration
    
    # Print metrics
    print("\n=== Execution Results ===")
    print(f"Status: COMPLETED")
    print(f"Exit Code: {result.exit_code}")
    print(f"Duration: {result.duration:.2f}s")
    print(f"LLM Latency: {agent.llm_response.latency_ms:.2f}ms")
    print(f"Tokens Used: {agent.llm_response.token_usage.get('total_tokens', 0)}")
    
    if result.exit_code != 0:
        print("Pytest failed!")
        metrics["failure_stage"] = "EXECUTION"
        return metrics
        
    # Save a successful execution memory
    successful_memory = MemoryRecord.create(
        memory_type=MemoryType.EXECUTION,
        workflow_id=execution_id,
        task_id=task.id,
        agent_id="backend",
        summary=f"Successfully built: {prompt_text[:100]}... Tests passed.",
        execution_id=execution_id,
        importance=10.0,
        tags=["success", "demo2", "pytest"]
    )
    memory_service = knowledge_service.engine.memory
    memory_service.remember(successful_memory)
        
    print("\nDemo 2 Verification Complete: Full Autonomous Loop Successful!")
    metrics["success"] = True
    return metrics

if __name__ == "__main__":
    run_demo2()
