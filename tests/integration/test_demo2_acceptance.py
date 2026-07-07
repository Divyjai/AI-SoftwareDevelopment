import pytest
import hashlib
from pathlib import Path
from .demo2_context import Demo2AcceptanceContext
from app.domain.models.execution_phase import ExecutionPhase

DB_PATH = Path(__file__).parent.parent.parent / "demo2_artifacts.db"

class TestDemo2Acceptance:
    """
    Acceptance checklist for Demo 2 autonomous execution loop.
    Every run of Demo 2 must satisfy these criteria to be considered a success.
    """
    
    @pytest.fixture(scope="class")
    def context(self):
        try:
            return Demo2AcceptanceContext(DB_PATH)
        except ValueError as e:
            pytest.fail(f"Test setup failed: {str(e)}")

    def test_planning_completed(self, context):
        """Validates that planning and task generation occurred."""
        # 1. Check Project plan generated (via artifacts using explicit type)
        plan_artifacts = [a for a in context.artifacts if a.get('artifact_type') == 'PROJECT_PLAN']
        assert len(plan_artifacts) > 0, "No project plan artifact found."
        
        # 2. Check Tasks created and assigned (via events or DB)
        task_created_events = [e for e in context.events if e.get('event_type') == 'TASK_CREATED']
        task_assigned_events = [e for e in context.events if e.get('event_type') == 'TASK_ASSIGNED']
        assert len(task_created_events) > 0, "No tasks were created."
        assert len(task_assigned_events) > 0, "No tasks were assigned."

    def test_generation_completed(self, context):
        """Validates LLM interaction, code generation, and validation."""
        # 1. Prompt compiled & LLM response received
        assert len(context.prompts) > 0, "No prompts were compiled or sent to LLM."
        
        for prompt in context.prompts:
            assert prompt.get('compiled_prompt_checksum'), "Prompt checksum missing."
            assert prompt.get('prompt_template_version'), "Prompt template version missing."
            assert prompt.get('system_prompt_version'), "System prompt version missing."
        
        # 2. Files written & Validation passed
        files_written_events = [e for e in context.events if e.get('event_type') == 'FILES_WRITTEN']
        assert len(files_written_events) > 0, "Source code files were not written."
        
        validation_events = [e for e in context.events if e.get('event_type') == 'VALIDATION_PASSED']
        assert len(validation_events) > 0, "Validation did not pass."

    def test_execution_completed(self, context):
        """Validates workspace creation, dependencies, tests, and exit code."""
        # Check execution result exists
        assert context.execution is not None, "Execution result was not persisted."
        
        # 1. Exit code recorded and indicates success (0)
        assert context.execution.get('exit_code') == 0, "Execution failed or exit code not recorded."
        
        # 2. Execution phase transitions
        phase_value = context.execution.get('status')
        # Map back to enum to check
        try:
            # Depending on if it's saved as name or value
            if isinstance(phase_value, int) or str(phase_value).isdigit():
                phase = ExecutionPhase(int(phase_value))
            else:
                phase = ExecutionPhase[str(phase_value).upper()]
        except (ValueError, KeyError):
            pytest.fail(f"Invalid phase value persisted: {phase_value}")
            
        assert phase == ExecutionPhase.COMPLETED, f"Execution phase did not end in COMPLETED, got {phase.name}."
        
    def test_persistence_completed(self, context):
        """Validates artifacts and execution results are properly persisted."""
        # 1. ExecutionResult persisted
        assert context.execution is not None
        
        # 2. Artifacts persisted & integrity
        assert len(context.artifacts) > 0, "No artifacts were persisted."
        for artifact in context.artifacts:
            content = artifact.get('content', '')
            stored_checksum = artifact.get('checksum')
            if stored_checksum:
                actual_checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()
                assert actual_checksum == stored_checksum, f"Artifact checksum mismatch for {artifact.get('id')}"

    def test_observability_completed(self, context):
        """Validates event emission, event ordering, and phase transitions."""
        # Check events emitted
        assert len(context.events) > 0, "No events were emitted."
        
        # 1. Check exact event ordering for core lifecycle
        event_types = [e.get('event_type') for e in context.events]
        
        expected_lifecycle = [
            "TASK_CREATED",
            "TASK_ASSIGNED",
            "PROMPT_COMPILED",
            "CODE_GENERATED",
            "VALIDATION_PASSED",
            "EXECUTION_STARTED",
            "EXECUTION_COMPLETED"
        ]
        
        # Filter down to just the lifecycle events to ensure exact sequence
        actual_lifecycle = [e for e in event_types if e in expected_lifecycle]
        
        assert actual_lifecycle == expected_lifecycle, (
            f"Lifecycle events did not match expected exact order.\n"
            f"Expected: {expected_lifecycle}\n"
            f"Actual: {actual_lifecycle}"
        )
        
        # 2. Traceability Assertions
        execution_id = context.execution.get('execution_id')
        correlation_id = context.execution.get('correlation_id')
        
        if correlation_id:
            # Check all events have this correlation_id
            for e in context.events:
                assert e.get('correlation_id') == correlation_id, f"Traceability broken for event {e.get('id')}"
            
            # Check all artifacts have this correlation_id (or produced_by_task = execution_id)
            for a in context.artifacts:
                assert a.get('produced_by_task') == execution_id, f"Traceability broken for artifact {a.get('id')}"
                
            # Check all prompts
            for p in context.prompts:
                assert p.get('execution_id') == execution_id, f"Traceability broken for prompt {p.get('prompt_id')}"
                
        # 3. Phase Assertions
        phase_events = [e.get('details', {}).get('phase') for e in context.events if e.get('event_type') == 'PHASE_TRANSITION']
        if phase_events:
            expected_phases = [
                ExecutionPhase.VALIDATING.name,
                ExecutionPhase.PREPARING_WORKSPACE.name,
                ExecutionPhase.INSTALLING_DEPENDENCIES.name,
                ExecutionPhase.EXECUTING.name,
                ExecutionPhase.COLLECTING_RESULTS.name,
                ExecutionPhase.PERSISTING_RESULTS.name,
                ExecutionPhase.COMPLETED.name
            ]
            assert phase_events == expected_phases, "Execution phases did not transition through the required sequence."

    def test_cleanup_completed(self, context):
        """Validates that the workspace was properly cleaned up."""
        manifest = context.manifest
        assert manifest is not None, "Workspace manifest not found."
        
        workspace_path = manifest.get('workspace_path')
        assert workspace_path is not None, "Workspace path not recorded in manifest."
        
        path = Path(workspace_path)
        assert not path.exists(), f"Workspace directory {workspace_path} was not cleaned up!"
