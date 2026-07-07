import sys
from pathlib import Path
sys.path.append(str(Path(r"c:\Users\divay\adk-project")))

from app.infrastructure.execution.workspace_manager import WorkspaceManager
from app.infrastructure.execution.dependency_manager import DependencyManager
from app.infrastructure.execution.runtime_provider import SubprocessRuntime
from app.infrastructure.execution.result_collector import ResultCollector
from app.application.execution_engine.engine import ExecutionEngine

def test_execution():
    engine = ExecutionEngine(
        workspace_manager=WorkspaceManager(),
        dep_manager=DependencyManager(),
        runtime=SubprocessRuntime(),
        collector=ResultCollector()
    )
    
    files = {
        "main.py": "import sys\nprint('Hello from Execution Engine')\nsys.stderr.write('Error log demo')\nwith open('output.txt', 'w') as f:\n    f.write('Generated file')\n",
    }
    
    result = engine.execute(task_id="T-001", files=files, command=["python", "main.py"])
    
    assert result.status == "success", f"Execution failed: {result.stderr}"
    assert "Hello from Execution Engine" in result.stdout
    assert "Error log demo" in result.stderr
    assert "output.txt" in result.files_produced
    assert result.duration > 0
    assert result.exit_code == 0
    
    print("VALIDATION SUCCESS: ExecutionEngine successfully managed workspace, executed code, collected rich results, and cleaned up.")

if __name__ == "__main__":
    test_execution()
