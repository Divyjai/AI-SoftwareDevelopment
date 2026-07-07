import pytest
import os
import shutil
import time
from app.application.knowledge.factory import KnowledgeFactory
from app.domain.models.task import Task
from app.domain.memory.models import MemoryRecord, MemoryType
from app.application.prompt_engine.prompt_compiler import PromptCompiler

@pytest.fixture(scope="module", autouse=True)
def setup_test_dbs():
    os.environ["LLM_PROVIDER"] = "ollama"
    
    # Clean up any test databases to start fresh
    test_dbs = ["test_knowledge_artifacts.db", "test_chroma_db_knowledge"]
    for db in test_dbs:
        if os.path.isdir(db):
            shutil.rmtree(db, ignore_errors=True)
        elif os.path.isfile(db):
            try:
                os.remove(db)
            except OSError:
                pass
                
    yield
    
    # Cleanup after
    for db in test_dbs:
        if os.path.isdir(db):
            shutil.rmtree(db, ignore_errors=True)
        elif os.path.isfile(db):
            try:
                os.remove(db)
            except OSError:
                pass

@pytest.mark.asyncio
async def test_knowledge_engine_flow():
    # 1. We mock out the factories just like we did in memory tests to use test dbs
    from app.infrastructure.chroma.vector_store import ChromaVectorStore
    from app.application.knowledge.factory import KnowledgeFactory
    
    original_create = KnowledgeFactory.create
    
    def mock_create(base_dir="."):
        svc = original_create(base_dir=base_dir)
        
        # Override with test paths
        svc.engine.memory.vector_store = ChromaVectorStore(persist_directory="test_chroma_db_knowledge")
        svc.engine.memory.repository.db_path = "test_knowledge_artifacts.db"
        svc.engine.memory.repository._init_db()
        svc.engine.memory.history.db_path = "test_knowledge_artifacts.db"
        svc.engine.memory.history._init_db()
        
        # Ensure we also override the new SQLite repos in the knowledge engine
        svc.engine.artifacts.conn.close() # Close default
        svc.engine.artifacts.__init__(db_path="test_knowledge_artifacts.db")
        
        svc.engine.executions.db_path = "test_knowledge_artifacts.db"
        svc.engine.retrieval_history.db_path = "test_knowledge_artifacts.db"
        svc.engine.retrieval_history._init_db()
        
        if hasattr(svc.engine.memory.embedding_client, 'cache'):
            svc.engine.memory.embedding_client.cache.db_path = "test_knowledge_artifacts.db"
            svc.engine.memory.embedding_client.cache._init_db()
            
        return svc
        
    KnowledgeFactory.create = staticmethod(mock_create)
    
    try:
        knowledge_service = KnowledgeFactory.create()
    
        # 2. Simulate Todo API memory generation
        todo_memory = MemoryRecord.create(
            memory_type=MemoryType.EXECUTION,
            workflow_id="wf-1",
            task_id="task-todo",
            agent_id="backend",
            summary="Implementation of Todo API using FastAPI with full tests.",
            tags=["fastapi", "todo"]
        )
        knowledge_service.engine.memory.remember(todo_memory)
        
        time.sleep(0.1) # Small pause for sqlite ordering
        
        # 3. Request Notes API generation
        task = Task(id="task-notes", description="Build a Notes API with FastAPI.")
        
        bundle = knowledge_service.build_context(
            task=task,
            agent_name="backend",
            manager_name="backend_manager",
            execution_id="test-exec-1"
        )
        
        # 4. Verify the KnowledgeBundle retrieved the Todo API memory
        assert bundle is not None
        assert bundle.current_task.id == "task-notes"
        
        # We should have at least 1 memory
        assert len(bundle.relevant_memories) > 0
        assert bundle.relevant_memories[0].summary == "Implementation of Todo API using FastAPI with full tests."
        assert bundle.retrieval_metadata is not None
        
        # 5. Pass bundle to PromptCompiler
        compiler = PromptCompiler(base_dir=".")
        compiled_prompt = compiler.compile(bundle)
        
        # Verify the memory string is injected properly
        assert "Implementation of Todo API" in compiled_prompt.rendered_prompt
        assert "Build a Notes API" in compiled_prompt.rendered_prompt
        
    finally:
        KnowledgeFactory.create = original_create
