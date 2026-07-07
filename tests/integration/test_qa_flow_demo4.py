import os
import tempfile
from pathlib import Path
from app.application.qa.qa_engine import QAEngine
from app.shared.state.project_state import ProjectState
from app.domain.models.project_graph import ProjectGraph, GraphNode, NodeType, CoverageStatus
from app.domain.models.qa import TestExecutionResult

class MockExecutionEngine:
    pass

class MockRepairEngine:
    def __init__(self):
        self.repaired = False
    
    def run_repair(self, execution_id: str, raw_failure_output: str):
        self.repaired = True

class MockMemoryService:
    pass

class MockTestRunner:
    def __init__(self):
        self.call_count = 0
    
    def run_tests(self, test_paths):
        self.call_count += 1
        from app.domain.models.qa import TestExecutionResult
        from app.domain.models.repair import FailureReport
        
        # On first run, it fails
        if self.call_count == 1:
            report = FailureReport(
                failure_type="PytestFailure",
                root_cause="Assertion Failed",
                severity="HIGH",
                affected_files=["tests/test_get_todos.py"],
                affected_nodes=[],
                stack_trace="E AssertionError: [] != {'status': 'ok'}",
                suggested_strategy="",
                confidence=1.0,
                is_deterministic=True
            )
            return TestExecutionResult(
                passed=False,
                failed=True,
                skipped=False,
                duration=0.1,
                coverage=0.0,
                failure_reports=[report]
            )
        else:
            # On second run (after repair), it passes
            return TestExecutionResult(
                passed=True,
                failed=False,
                skipped=False,
                duration=0.1,
                coverage=1.0,
                failure_reports=[]
            )

def test_qa_flow_demo4():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create an uncovered function node
        graph = ProjectGraph()
        func_node = GraphNode(
            id="func:get_todos",
            type=NodeType.FUNCTION,
            name="get_todos",
            file_path="app/api.py",
            coverage_status=CoverageStatus.UNCOVERED
        )
        graph.add_node(func_node)
        
        state = ProjectState()
        state.graph = graph
        
        repair_engine = MockRepairEngine()
        qa_engine = QAEngine(
            workspace_path=temp_dir,
            execution_engine=MockExecutionEngine(),
            repair_engine=repair_engine,
            memory_service=MockMemoryService(),
            project_state=state
        )
        
        # Replace the real test runner with our mock that simulates a failure then a pass
        mock_runner = MockTestRunner()
        qa_engine.test_runner = mock_runner
        
        result = qa_engine.run_qa_cycle(context=None)
        
        # QA engine should have passed after repair
        assert result is True
        
        # TestRunner should have been called 3 times (loop 1 fail, loop 2 pass, final check)
        assert mock_runner.call_count == 3
        
        # Repair Engine should have been invoked
        assert repair_engine.repaired is True
        
        # Coverage analyzer should have updated the graph
        assert func_node.coverage_status == CoverageStatus.COVERED
        
        # A test artifact should have been created
        test_file = Path(temp_dir) / "tests" / "test_get_todos.py"
        assert test_file.exists()
