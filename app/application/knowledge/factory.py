from .engine import KnowledgeEngine
from .service import KnowledgeService
from .ranking import KnowledgeRanker
from .assembler import KnowledgeAssembler
from app.application.memory.factory import MemoryFactory
from app.infrastructure.repositories.sqlite_artifact_repository import SQLiteArtifactRepository
from app.infrastructure.sqlite.execution_repository import SQLiteExecutionRepository
from app.infrastructure.sqlite.retrieval_history_repository import SQLiteRetrievalHistoryRepository
from app.infrastructure.memory.project_repository import InMemoryProjectRepository

class KnowledgeFactory:
    @staticmethod
    def create(base_dir: str = ".") -> KnowledgeService:
        memory_service = MemoryFactory.create()
        artifact_repo = SQLiteArtifactRepository()
        execution_repo = SQLiteExecutionRepository()
        retrieval_repo = SQLiteRetrievalHistoryRepository()
        project_repo = InMemoryProjectRepository()
        
        ranker = KnowledgeRanker()
        assembler = KnowledgeAssembler(base_dir=base_dir)
        
        engine = KnowledgeEngine(
            memory_service=memory_service,
            artifact_repo=artifact_repo,
            execution_repo=execution_repo,
            project_repo=project_repo,
            retrieval_repo=retrieval_repo,
            ranker=ranker,
            assembler=assembler
        )
        
        return KnowledgeService(engine=engine)
