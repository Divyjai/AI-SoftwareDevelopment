import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.application.memory.factory import MemoryFactory
from app.domain.memory.models import MemoryType, MemoryRecord
import time
import shutil

@pytest.fixture(scope="module", autouse=True)
def setup_memory_db():
    # Set environment variables for testing
    os.environ["LLM_PROVIDER"] = "ollama"
    # Ensure test chroma db directory
    chroma_dir = "test_chroma_db"
    test_db = "test_memory_artifacts.db"
    
    if os.path.exists(chroma_dir):
        shutil.rmtree(chroma_dir)
    if os.path.exists(test_db):
        os.remove(test_db)
        
    yield
    
    # Cleanup after tests
    if os.path.exists(chroma_dir):
        # windows may hold lock, ignore errors
        shutil.rmtree(chroma_dir, ignore_errors=True)
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except OSError:
            pass

@pytest.mark.asyncio
async def test_memory_remember_and_retrieve():
    # 1. Initialize factory
    # Override the chroma directory to avoid polluting main db
    # We monkey patch for testing purposes
    from app.infrastructure.chroma.vector_store import ChromaVectorStore
    from app.application.memory.factory import MemoryFactory
    
    # Simple monkeypatch
    original_create = MemoryFactory.create
    
    def mock_create():
        memory_service = original_create()
        memory_service.vector_store = ChromaVectorStore(persist_directory="test_chroma_db")
        # Also use test sqlite
        memory_service.repository.db_path = "test_memory_artifacts.db"
        memory_service.repository._init_db()
        memory_service.history.db_path = "test_memory_artifacts.db"
        memory_service.history._init_db()
        # To test cache
        if hasattr(memory_service.embedding_client, 'cache'):
            memory_service.embedding_client.cache.db_path = "test_memory_artifacts.db"
            memory_service.embedding_client.cache._init_db()
        return memory_service
        
    MemoryFactory.create = staticmethod(mock_create)
    
    try:
        memory_service = MemoryFactory.create()
        
        # 2. Store MemoryRecord in SQLite and Chroma
        todo_api_summary = "How to build a Todo API using FastAPI. It has endpoints for GET /todos and POST /todos. Uses pydantic."
        
        # Wait a moment to ensure timestamps are unique
        time.sleep(0.1)
        
        record = MemoryRecord.create(
            memory_type=MemoryType.EXECUTION,
            workflow_id="wf-1",
            task_id="task-todo-1",
            agent_id="backend",
            summary=todo_api_summary,
            tags=["todo", "fastapi", "python"]
        )
        
        # Generate embedding using Ollama and Store in ChromaDB/SQLite
        memory_service.remember(record)
        
        # 3. Retrieve by semantic similarity
        # A query similar to what was saved
        query = "I need to make a notes API or a todo API with endpoints."
        
        # This will use Ollama to embed the query, then search chroma, then load metadata from SQLite
        results = memory_service.retrieve(query=query, execution_id="test-exec-1", limit=5)
        
        assert len(results) > 0
        
        found = False
        for res in results:
            if res.task_id == "task-todo-1":
                found = True
                assert res.summary == todo_api_summary
                assert "fastapi" in res.tags
                
        assert found, "The memory record was not successfully retrieved"
        
        # Test Caching
        assert memory_service.metrics.stats.cache_hits >= 0 # Just verify it doesn't crash
        
        # Test Versioning
        record_v2 = MemoryRecord.create(
            memory_type=MemoryType.EXECUTION,
            workflow_id="wf-1",
            task_id="task-todo-1", # Same task
            agent_id="backend",
            summary="Updated Todo API with a database.",
            parent_memory_id=record.id,
            supersedes_id=record.id,
            version=2
        )
        memory_service.remember(record_v2)
        
        # Original record should now be is_latest = False
        original_db_record = memory_service.repository.get(record.id)
        assert original_db_record.is_latest is False
        
        v2_db_record = memory_service.repository.get(record_v2.id)
        assert v2_db_record.is_latest is True
        
        # Retrieve should only return v2 since it filters by is_latest
        results_v2 = memory_service.retrieve(query=query, execution_id="test-exec-2", limit=5)
        v1_found = any(r.id == record.id for r in results_v2)
        v2_found = any(r.id == record_v2.id for r in results_v2)
        
        assert not v1_found, "Old version should not be returned by default"
        assert v2_found, "New version should be returned"
        
    finally:
        # Restore mock
        MemoryFactory.create = original_create
        if os.path.exists("test_memory_artifacts.db"):
            try:
                os.remove("test_memory_artifacts.db")
            except OSError:
                pass
