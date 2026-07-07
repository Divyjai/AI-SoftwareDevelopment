from pathlib import Path
import os
from app.application.agents.qa_agent import QAAgent
from app.application.qa.test_runner import TestRunner
from app.application.qa.failure_classifier import FailureClassifier
from app.application.qa.coverage_analyzer import CoverageAnalyzer
from app.domain.models.qa import FailureClassification, TestMemory
from app.domain.models.project_graph import EdgeType, GraphEdge

class QAEngine:
    def __init__(self, workspace_path: str, execution_engine, repair_engine, memory_service, project_state):
        self.workspace_path = Path(workspace_path)
        self.execution_engine = execution_engine
        self.repair_engine = repair_engine
        self.memory_service = memory_service
        self.project_state = project_state
        
        self.qa_agent = QAAgent()
        self.test_runner = TestRunner(execution_engine)
        self.classifier = FailureClassifier()
        self.coverage_analyzer = CoverageAnalyzer()

    def run_qa_cycle(self, context) -> bool:
        # 1. Discover and generate tests
        test_artifacts = self.qa_agent.run(context, self.project_state.graph)
        if not test_artifacts:
            # Everything is covered
            return True
            
        # 2. Write tests to filesystem
        tests_dir = self.workspace_path / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        test_paths = []
        for artifact in test_artifacts:
            file_path = self.workspace_path / artifact.metadata["path"]
            # Ensure parent directories exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(artifact.content)
            test_paths.append(artifact.metadata["path"])
            
            # Update graph linking the new test to the targeted node
            test_node_id = f"test:{artifact.metadata['target_node']}"
            # This is a naive way to register the test in the graph for demo purposes
            # Normally project parser would detect the new file
            from app.domain.models.project_graph import GraphNode, NodeType
            self.project_state.graph.add_node(GraphNode(
                id=test_node_id,
                type=NodeType.TEST,
                name=f"test_for_{artifact.metadata['target_node']}",
                file_path=artifact.metadata["path"]
            ))
            
            self.project_state.graph.add_edge(GraphEdge(
                source_id=test_node_id,
                target_id=artifact.metadata["target_node"],
                type=EdgeType.TESTS
            ))
            
        # 3. Execute tests
        # We will loop in case we need to repair
        max_qa_loops = 3
        for attempt in range(max_qa_loops):
            execution_result = self.test_runner.run_tests(test_paths)
            
            if execution_result.passed:
                break
                
            # 4. Classify Failures
            for report in execution_result.failure_reports:
                classification = self.classifier.classify(report)
                
                if classification == FailureClassification.APPLICATION:
                    # 5a. Application Bug -> Hand off to Repair Engine
                    # We pass the raw output associated with this failure to the repair engine
                    # (In a real system, the runner slices the output per test)
                    self.repair_engine.run_repair(
                        execution_id=f"qa-exec-{attempt}",
                        raw_failure_output=report.stack_trace
                    )
                elif classification == FailureClassification.TEST:
                    # 5b. Test Bug -> QAAgent regenerates
                    # We would ask QAAgent to rewrite the specific test file
                    pass
                else:
                    # Env or Dependency -> escalated
                    pass
                    
        # 6. Final execution to check status
        final_result = self.test_runner.run_tests(test_paths)
        
        # 7. Coverage Analysis & Graph Update
        # Normally project_parser runs here again
        self.coverage_analyzer.analyze(self.project_state.graph)
        
        # 8. Store Memory
        for artifact in test_artifacts:
            memory = TestMemory(
                endpoint=artifact.metadata["target_node"],
                generated_test=artifact.content,
                repair_count=0, # Would track actual repairs
                final_status="PASSED" if final_result.passed else "FAILED",
                coverage=final_result.coverage
            )
            # self.memory_service.save(memory)
            
        return final_result.passed
