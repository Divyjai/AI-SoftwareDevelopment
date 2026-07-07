import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from app.application.execution_engine.engine import ExecutionEngine
from app.domain.models.execution_phase import ExecutionPhase

def test_execution_engine_success():
    mock_workspace_mgr = Mock()
    mock_workspace_mgr.create_workspace.return_value = Path("/tmp/mock_ws")
    
    mock_dep_mgr = Mock()
    mock_dep_mgr.install_dependencies.return_value = ["fastapi", "uvicorn"]
    
    mock_runtime = Mock()
    mock_runtime.execute.return_value = (0, "success stdout", "")
    
    mock_collector = Mock()
    mock_collector.collect.return_value = Mock(
        status=ExecutionPhase.COMPLETED,
        python_version="3.9",
        os_name="Linux"
    )
    
    engine = ExecutionEngine(
        workspace_manager=mock_workspace_mgr,
        dep_manager=mock_dep_mgr,
        runtime=mock_runtime,
        collector=mock_collector
    )
    
    files = {"main.py": "print('hello')", "requirements.txt": "fastapi"}
    result = engine.execute("task_123", files, ["python", "main.py"])
    
    # Verify collector was called properly
    assert mock_collector.collect.called
    kwargs = mock_collector.collect.call_args[1]
    assert kwargs["phase"] == ExecutionPhase.COMPLETED
    assert result.status == ExecutionPhase.COMPLETED

def test_execution_engine_dependency_failure():
    mock_workspace_mgr = Mock()
    mock_workspace_mgr.create_workspace.return_value = Path("/tmp/mock_ws")
    
    mock_dep_mgr = Mock()
    mock_dep_mgr.install_dependencies.side_effect = Exception("pip install failed")
    
    mock_runtime = Mock()
    mock_collector = Mock()
    
    engine = ExecutionEngine(
        workspace_manager=mock_workspace_mgr,
        dep_manager=mock_dep_mgr,
        runtime=mock_runtime,
        collector=mock_collector
    )
    
    files = {"main.py": "print('hello')", "requirements.txt": "invalid_package"}
    engine.execute("task_123", files, ["python", "main.py"])
    
    # Should catch exception and call collector with INSTALLING_DEPENDENCIES phase
    assert mock_collector.collect.called
    kwargs = mock_collector.collect.call_args[1]
    assert kwargs["phase"] == ExecutionPhase.INSTALLING_DEPENDENCIES
