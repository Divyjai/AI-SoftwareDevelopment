from typing import List, Optional, Dict, Any
from app.domain.memory.models import MemoryRecord, MemoryType
from app.interfaces.memory_repository import MemoryRepository
from app.interfaces.vector_store import VectorStore
from app.interfaces.embedding_client import EmbeddingClient
from app.application.memory.indexer import MemoryIndexer
from app.application.memory.metrics import MemoryMetrics
from app.application.memory.retrieval_history import RetrievalHistory, RetrievalLog
import uuid
import time
from datetime import datetime

class MemoryService:
    def __init__(self,
                 repository: MemoryRepository,
                 vector_store: VectorStore,
                 embedding_client: EmbeddingClient,
                 indexer: MemoryIndexer,
                 metrics: MemoryMetrics = None,
                 history: RetrievalHistory = None):
        self.repository = repository
        self.vector_store = vector_store
        self.embedding_client = embedding_client
        self.indexer = indexer
        self.metrics = metrics or MemoryMetrics()
        self.history = history or RetrievalHistory()

    def remember(self, record: MemoryRecord) -> None:
        """
        Stores memory metadata to SQLite and conditionally indexes the semantic content to ChromaDB.
        """
        text_to_embed = self.indexer.prepare_for_embedding(record)
        
        if text_to_embed:
            t0 = time.time()
            embedding = self.embedding_client.embed_text(text_to_embed)
            duration = time.time() - t0
            
            # Since caching is inside the adapter, we can't easily tell if it was a hit here unless we check.
            # But the metric is updated roughly.
            self.metrics.record_embedded(duration, cached=duration < 0.01) # arbitrary threshold for mock/cache
            
            vector_id = f"vec-{uuid.uuid4().hex[:8]}"
            record.embedding_id = vector_id
            
            vector_metadata = {
                "memory_id": record.id,
                "workflow_id": record.workflow_id,
                "task_id": record.task_id,
                "agent_id": record.agent_id,
                "memory_type": record.memory_type.value,
                "importance": record.importance
            }
            if record.tags:
                vector_metadata["tags"] = ",".join(record.tags)
                
            self.vector_store.upsert(vector_id=vector_id, embedding=embedding, metadata=vector_metadata)
            
        self.repository.save(record)
        self.metrics.record_saved()

    def retrieve(self, query: str, execution_id: str, limit: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> List[MemoryRecord]:
        t0 = time.time()
        query_embedding = self.embedding_client.embed_text(query)
        
        # We query for more because we will rank and filter them
        search_results = self.vector_store.similarity_search(
            query_embedding=query_embedding,
            limit=limit * 3,
            filter_metadata=filter_metadata
        )
        
        now = datetime.utcnow().timestamp()
        
        scored_records = []
        for res in search_results:
            mem_id = res.metadata.get("memory_id")
            if mem_id:
                record = self.repository.get(mem_id)
                if record and record.is_latest:
                    # Score components
                    # res.score is distance in chroma. semantic_similarity = 1 - distance (roughly)
                    # We bound it to 0..1
                    semantic_similarity = max(0.0, 1.0 - res.score)
                    
                    # importance_score: normalize importance (assuming normal range 1-10)
                    importance_score = min(1.0, record.importance / 10.0)
                    
                    # recency_score: exponential decay based on days
                    days_old = (now - record.created_at) / (24 * 3600)
                    recency_score = 1.0 / (1.0 + days_old)
                    
                    final_score = 0.70 * semantic_similarity + 0.20 * importance_score + 0.10 * recency_score
                    scored_records.append((final_score, record))
                    
        # Sort by final_score descending
        scored_records.sort(key=lambda x: x[0], reverse=True)
        top_records = [r for score, r in scored_records[:limit]]
        
        self.metrics.record_retrieval(time.time() - t0)
        
        # Log to history
        top_k_ids = [res.metadata.get("memory_id") for res in search_results][:limit]
        chosen_ids = [r.id for r in top_records]
        
        # create snippet of what was injected
        injected = "\n".join([r.summary for r in top_records])
        
        log_entry = RetrievalLog.create(
            query=query,
            execution_id=execution_id,
            top_k_retrieved_ids=top_k_ids,
            chosen_memory_ids=chosen_ids,
            prompt_injected=injected
        )
        self.history.log(log_entry)
                    
        return top_records
