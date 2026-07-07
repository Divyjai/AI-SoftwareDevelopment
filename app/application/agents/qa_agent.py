from app.domain.models.agent import BaseAgent
from app.domain.models.agent_context import AgentContext
from app.domain.models.project_graph import CoverageStatus, ProjectGraph
from app.domain.models.artifact import Artifact, ArtifactState
import json

class QAAgent(BaseAgent):
    def __init__(self):
        self.context = None
        self.uncovered_nodes = []
        self.generated_tests = []

    def run(self, context: AgentContext, project_graph: ProjectGraph):
        self.prepare(context)
        self.discover(project_graph)
        self.plan()
        self.act()
        self.validate()
        return self.report()

    def prepare(self, context: AgentContext):
        self.context = context

    def discover(self, project_graph: ProjectGraph):
        # Find all uncovered nodes prioritizing FUNCTIONS then ENDPOINTS
        self.uncovered_nodes = []
        for node in project_graph.nodes.values():
            if node.type.name in ["FUNCTION", "ENDPOINT"] and node.coverage_status == CoverageStatus.UNCOVERED:
                self.uncovered_nodes.append(node)
                
        # Sort so we do unit tests (FUNCTION) before integration tests (ENDPOINT),
        # but primarily sort by risk score (descending) so high risk is tested first.
        self.uncovered_nodes.sort(
            key=lambda x: (
                -x.risk_metrics.risk_score, # Highest risk first
                0 if x.type.name == "FUNCTION" else 1 # Unit tests before integration
            )
        )

    def plan(self):
        # We would use KnowledgeEngine to build context around these uncovered nodes
        pass

    def act(self):
        # Generate tests for each uncovered node
        # We simulate the LLM output for demonstration purposes
        for node in self.uncovered_nodes:
            # We mock the generated code
            test_content = f"""
def test_{node.name}():
    # Auto-generated test for {node.name}
    assert True
"""
            # Create a mock artifact representing the test file
            file_name = f"tests/test_{node.name}.py"
            
            artifact = Artifact(
                id=f"art-test-{node.name}",
                version="v1",
                owner="qa",
                status=ArtifactState.GENERATED,
                content=test_content,
                produced_by_task="qa-task",
                metadata={"path": file_name, "target_node": node.id}
            )
            setattr(artifact, 'artifact_type', 'SOURCE_FILE')
            self.generated_tests.append(artifact)

    def validate(self):
        assert len(self.generated_tests) == len(self.uncovered_nodes)

    def report(self):
        # Returns the artifacts so QAEngine can save them and execute them
        return self.generated_tests

