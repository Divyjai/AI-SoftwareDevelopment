from typing import List
from app.interfaces.embedding_client import EmbeddingClient
from app.infrastructure.ollama.client import OllamaClient
from app.infrastructure.sqlite.embedding_cache import SQLiteEmbeddingCache
import time

class OllamaEmbeddingAdapter(EmbeddingClient):
    def __init__(self, ollama_client: OllamaClient, cache: SQLiteEmbeddingCache = None):
        self._client = ollama_client.get_client()
        self.embedding_model = ollama_client.config.embedding_model
        self.cache = cache or SQLiteEmbeddingCache()

    def embed_text(self, text: str) -> List[float]:
        cached = self.cache.get(text)
        if cached:
            return cached
            
        response = self._client.embeddings(model=self.embedding_model, prompt=text)
        embedding = response.get("embedding", [])
        
        if embedding:
            self.cache.set(text, embedding)
            
        return embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(text) for text in texts]
