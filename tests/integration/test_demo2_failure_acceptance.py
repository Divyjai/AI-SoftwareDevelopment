import pytest
from pathlib import Path
from .demo2_context import Demo2AcceptanceContext

DB_PATH = Path(__file__).parent.parent.parent / "demo2_artifacts.db"

class TestDemo2FailureAcceptance:
    """
    Validates that the system handles failures gracefully during Demo 2 execution.
    These tests would typically run against specific failure injection scenarios.
    """
    
    @pytest.fixture(scope="class")
    def syntax_error_context(self):
        # In a real test suite, this would fetch an execution explicitly known to be a syntax error
        # e.g., execution_id = "test-fail-syntax-123"
        # Since we don't have this execution seeded yet, we will skip if not found rather than picking latest
        execution_id = "deterministic-syntax-failure-id"
        try:
            return Demo2AcceptanceContext(DB_PATH, execution_id=execution_id)
        except ValueError:
            pytest.skip(f"No syntax error execution found in database with id {execution_id}.")

    @pytest.fixture(scope="class")
    def dependency_failure_context(self):
        execution_id = "deterministic-dependency-failure-id"
        try:
            return Demo2AcceptanceContext(DB_PATH, execution_id=execution_id)
        except ValueError:
            pytest.skip(f"No dependency failure execution found in database with id {execution_id}.")

    @pytest.fixture(scope="class")
    def timeout_failure_context(self):
        execution_id = "deterministic-timeout-failure-id"
        try:
            return Demo2AcceptanceContext(DB_PATH, execution_id=execution_id)
        except ValueError:
            pytest.skip(f"No timeout execution found in database with id {execution_id}.")

    def test_validation_failure_recorded(self, syntax_error_context):
        """Validates that a syntax error correctly fails the validation phase."""
        execution = syntax_error_context.execution
        assert execution.get('exit_code') != 0, "Execution should have failed."
        
        phase = execution.get('status')
        assert str(phase).upper() in ["VALIDATING", "FAILED", "2"], "Failure should be recorded during validation phase."

    def test_dependency_failure_recorded(self, dependency_failure_context):
        """Validates that an invalid package correctly fails the dependency installation phase."""
        execution = dependency_failure_context.execution
        assert execution.get('exit_code') != 0, "Execution should have failed."
        
        phase = execution.get('status')
        assert str(phase).upper() in ["INSTALLING_DEPENDENCIES"], "Failure should be recorded during dependency phase."

    def test_execution_timeout_recorded(self, timeout_failure_context):
        """Validates that an infinite loop correctly fails the execution phase with a timeout."""
        execution = timeout_failure_context.execution
        assert execution.get('exit_code') == -1, "Execution should have timed out with -1 exit code."
        
        phase = execution.get('status')
        assert str(phase).upper() in ["EXECUTING"], "Timeout should be recorded during executing phase."

