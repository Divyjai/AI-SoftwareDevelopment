from pathlib import Path
from typing import Optional, List, Dict, Any
from app.domain.models.task import Task
from app.shared.state.project_state import ProjectState
from app.domain.memory.models import MemoryRecord
from app.domain.models.artifact import Artifact
from .bundle import KnowledgeBundle, RetrievalMetadata

class KnowledgeAssembler:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)

    def assemble(self,
                 goal: str,
                 task: Task,
                 agent_name: str,
                 manager_name: str,
                 memories: List[MemoryRecord],
                 artifacts: List[Artifact],
                 executions: List[Dict[str, Any]],
                 failures: List[MemoryRecord],
                 project_state: Optional[ProjectState],
                 metadata: RetrievalMetadata) -> KnowledgeBundle:
        
        system_context = self._get_system_context()
        workflow = self._get_workflow_context()
        agent_settings = {"agent_name": agent_name, "manager_name": manager_name}
        
        project_summary = ""
        if project_state:
            project_summary = f"Branch: {project_state.branch}\nMetrics: {project_state.metrics}"

        return KnowledgeBundle(
            goal=goal,
            workflow=workflow,
            project="",
            current_task=task,
            project_summary=project_summary,
            relevant_memories=memories,
            artifacts=artifacts,
            execution_history=executions,
            similar_failures=failures,
            constraints=[],
            agent_settings=agent_settings,
            system_context=system_context,
            retrieval_metadata=metadata,
            project_graph=project_state.graph if project_state else None,
            relevant_nodes=[] # Engine will fill this or we can leave empty
        )

    def _get_system_context(self) -> str:
        content = []
        for f in ["system_context.md", "architecture.md", "engineering_rules.md", "workflow.md"]:
            p = self.base_dir / "app/context/system" / f
            if p.exists():
                content.append(p.read_text())
        return "\n\n".join(content)

    def _get_workflow_context(self) -> str:
        p = self.base_dir / "app/context/system/workflow.md"
        return p.read_text() if p.exists() else ""
