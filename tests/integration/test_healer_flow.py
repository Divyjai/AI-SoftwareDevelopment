import os
import tempfile
from pathlib import Path
from app.application.repair.engine import RepairEngine
from app.shared.state.project_state import ProjectState
from app.domain.models.project_graph import ProjectGraph, GraphNode, NodeType
from app.application.knowledge.project_parser import PythonProjectParser

# Simple mocks for dependencies
class MockExecutionEngine:
    pass

class MockKnowledgeService:
    pass

class MockMemoryService:
    pass

def test_healer_flow_demo3():
    with tempfile.TemporaryDirectory() as temp_dir:
        app_dir = Path(temp_dir) / "app"
        app_dir.mkdir()
        
        api_file = app_dir / "api.py"
        with open(api_file, "w") as f:
            f.write("""
def get_todos():
    # intentional bug
    1 / 0
    return []
""")
        
        # 1. Parse project graph
        parser = PythonProjectParser(workspace_path=temp_dir)
        graph = parser.parse()
        
        state = ProjectState()
        state.graph = graph
        
        # 2. Setup engine
        engine = RepairEngine(
            workspace_path=temp_dir,
            execution_engine=MockExecutionEngine(),
            knowledge_service=MockKnowledgeService(),
            memory_service=MockMemoryService(),
            project_state=state
        )
        
        # 3. Simulate a failure report
        raw_error = f'''Traceback (most recent call last):
  File "{api_file.relative_to(temp_dir)}", line 4, in get_todos
    1 / 0
ZeroDivisionError: division by zero
'''
        
        session = engine.run_repair(execution_id="exec-123", raw_failure_output=raw_error)
        
        assert session.status == "SUCCESS"
        assert len(session.patches) == 1
        
        patch = session.patches[0]
        assert patch.change_type == "REPLACE"
        
        # Check if the file was modified
        with open(api_file, "r") as f:
            content = f.read()
            
        assert "1 / 0" not in content
        assert "return {'status': 'ok'}" in content
