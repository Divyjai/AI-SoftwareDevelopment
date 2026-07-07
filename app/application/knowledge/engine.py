import time
from typing import Optional, Dict
from app.domain.models.task import Task
from app.interfaces.artifact_repository import ArtifactRepository
from app.interfaces.execution_repository import ExecutionRepository
from app.interfaces.project_repository import ProjectRepository
from app.interfaces.retrieval_history_repository import RetrievalHistoryRepository
from app.application.memory.service import MemoryService
from .bundle import KnowledgeBundle, RetrievalMetadata
from .ranking import KnowledgeRanker
from .assembler import KnowledgeAssembler

class KnowledgeEngine:
    def __init__(self, 
                 memory_service: MemoryService,
                 artifact_repo: ArtifactRepository,
                 execution_repo: ExecutionRepository,
                 project_repo: ProjectRepository,
                 retrieval_repo: RetrievalHistoryRepository,
                 ranker: KnowledgeRanker,
                 assembler: KnowledgeAssembler):
        self.memory = memory_service
        self.artifacts = artifact_repo
        self.executions = execution_repo
        self.projects = project_repo
        self.retrieval_history = retrieval_repo
        self.ranker = ranker
        self.assembler = assembler

    def build_context(self, task: Task, agent_name: str, manager_name: str, execution_id: str) -> KnowledgeBundle:
        start_time = time.time()
        
        # 1. Fetch raw candidates
        memories = self.memory.retrieve(query=task.description, execution_id=execution_id, limit=20)
        artifacts = self.artifacts.get_recent_artifacts(limit=20)
        executions = self.executions.get_recent_executions(limit=10)
        failures = self.memory.retrieve(query=task.description, execution_id=execution_id, limit=10, filter_metadata={"status": "failed"}) # Just an example filter
        project_state = self.projects.get_project_state()
        
        # 2. Rank and Trim to Top K
        top_memories = self.ranker.rank_memories(memories, top_k=10)
        top_artifacts = self.ranker.rank_artifacts(artifacts, task, top_k=5)
        top_executions = self.ranker.rank_executions(executions, top_k=5)
        top_failures = self.ranker.rank_memories(failures, top_k=5)
        
        # 3. Build Metadata
        avg_sim = 0.0
        # Compute avg similarity if we have that metric, currently not exposed directly on MemoryRecord,
        # but we could approximate or add it. Let's default to 0 for now.
        
        duration = time.time() - start_time
        metadata = RetrievalMetadata(
            memory_count=len(top_memories),
            artifact_count=len(top_artifacts),
            execution_count=len(top_executions),
            average_similarity=avg_sim,
            retrieval_duration=duration,
            strategy="semantic_hybrid"
        )
        
        # Log to repository
        # Just logging memory ids for now
        mem_ids = [m.id for m in top_memories]
        self.retrieval_history.log_retrieval(
            query=task.description,
            execution_id=execution_id,
            returned_ids=mem_ids,
            scores=[], # Not passing scores here
            metadata={"strategy": metadata.strategy, "duration": metadata.retrieval_duration}
        )
        
        # 4. Assemble Bundle
        bundle = self.assembler.assemble(
            goal=task.description,
            task=task,
            agent_name=agent_name,
            manager_name=manager_name,
            memories=top_memories,
            artifacts=top_artifacts,
            executions=top_executions,
            failures=top_failures,
            project_state=project_state,
            metadata=metadata
        )
        
        # 5. Graph relevant nodes
        if bundle.project_graph:
            # simple heuristic: if task description mentions a file name, grab its node and blast radius
            for node in bundle.project_graph.nodes.values():
                if node.name in task.description:
                    bundle.relevant_nodes.append(node)
                    bundle.relevant_nodes.extend(bundle.project_graph.get_blast_radius(node.id))
        
        return bundle
