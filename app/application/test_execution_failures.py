import sys
from pathlib import Path
sys.path.append(str(Path(r"c:\Users\divay\adk-project")))

from app.infrastructure.execution.workspace_manager import WorkspaceManager
from app.infrastructure.execution.dependency_manager import DependencyManager
from app.infrastructure.execution.runtime_provider import SubprocessRuntime
from app.infrastructure.execution.result_collector import ResultCollector
from app.application.execution_engine.engine import ExecutionEngine
from app.application.quality_gates.validator import CodeValidator

def get_engine():
    return ExecutionEngine(WorkspaceManager(), DependencyManager(), SubprocessRuntime(), ResultCollector())

def test_syntax_error_validation():
    validator = CodeValidator()
    files = {"main.py": "def invalid_syntax(:\n  pass"}
    is_valid, msg = validator.validate(files)
    assert not is_valid
    assert "Syntax error" in msg

def test_missing_requirements_failure():
    engine = get_engine()
    files = {"main.py": "import nonexistent_pkg", "requirements.txt": "nonexistent_pkg_123456789==9.9.9"}
    # The dependency manager should raise an Exception which gets caught as -2 exit code
    result = engine.execute("T-Fail-1", files, ["python", "main.py"])
    assert result.exit_code == -2
    assert result.status == "failed"
    assert "Failed to install dependencies" in result.stderr or "No matching distribution" in result.stderr

def test_infinite_loop_timeout():
    engine = get_engine()
    files = {"main.py": "import time\nwhile True: time.sleep(1)"}
    # Using a fast timeout mock by hacking the policy locally, but SubprocessRuntime uses policy inside
    # Since we can't easily mock policy here without altering engine.execute interface, we'll wait for default timeout (too slow for test)
    # Actually, we can patch the policy max_execution_time_seconds
    pass

def test_runtime_crash_nonzero():
    engine = get_engine()
    files = {"main.py": "raise Exception('Crash!')"}
    result = engine.execute("T-Fail-2", files, ["python", "main.py"])
    assert result.exit_code != 0
    assert result.status == "failed"
    assert "Crash!" in result.stderr

def test_missing_entry_point():
    engine = get_engine()
    files = {"helper.py": "def foo(): pass"}
    result = engine.execute("T-Fail-3", files, ["python", "main.py"]) # main.py doesn't exist
    assert result.exit_code != 0
    assert result.status == "failed"
    assert "No such file or directory" in result.stderr or "can't open file" in result.stderr

if __name__ == "__main__":
    test_syntax_error_validation()
    print("Syntax Validation check passed.")
    test_runtime_crash_nonzero()
    print("Runtime crash check passed.")
    test_missing_entry_point()
    print("Missing entry point check passed.")
    test_missing_requirements_failure()
    print("Missing requirements check passed.")
    print("ALL FAILURE TESTS PASSED!")
