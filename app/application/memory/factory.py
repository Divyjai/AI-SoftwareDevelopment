import os
from app.application.memory.service import MemoryService
from app.application.memory.indexer import MemoryIndexer
from app.infrastructure.sqlite.memory_repository import SQLiteMemoryRepository
from app.infrastructure.chroma.vector_store import ChromaVectorStore
from app.application.llm.factory import LLMFactory
from app.application.memory.metrics import MemoryMetrics
from app.application.memory.retrieval_history import RetrievalHistory

class MemoryFactory:
    @staticmethod
    def create() -> MemoryService:
        # Resolve dependencies
        repository = SQLiteMemoryRepository()
        vector_store = ChromaVectorStore()
        indexer = MemoryIndexer()
        metrics = MemoryMetrics()
        history = RetrievalHistory()
        
        # We need an EmbeddingClient. We can get it from LLMFactory or environment
        # Currently our LLMFactory might just return LLMProvider. 
        # But for now, let's instantiate the OllamaEmbeddingAdapter since Ollama is default
        provider_name = os.environ.get("LLM_PROVIDER", "ollama").lower()
        if provider_name == "ollama":
            from app.infrastructure.ollama.client import OllamaClient
            from app.infrastructure.ollama.config import OllamaConfig
            from app.infrastructure.ollama.embedding_adapter import OllamaEmbeddingAdapter
            config = OllamaConfig.from_env()
            client = OllamaClient(config)
            embedder = OllamaEmbeddingAdapter(client)
        else:
            from app.infrastructure.google.embedding_adapter import GoogleEmbeddingAdapter
            api_key = os.environ.get("GEMINI_API_KEY")
            embedder = GoogleEmbeddingAdapter(api_key)

        return MemoryService(
            repository=repository,
            vector_store=vector_store,
            embedding_client=embedder,
            indexer=indexer,
            metrics=metrics,
            history=history
        )
