import chromadb
from typing import List, Dict, Any, Optional
from app.interfaces.vector_store import VectorStore, VectorSearchResult

class ChromaVectorStore(VectorStore):
    def __init__(self, persist_directory: str = "chroma_db", collection_name: str = "agent_memories"):
        self.persist_directory = persist_directory
        # using PersistentClient for local persistence
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"} # Use cosine similarity
        )

    def upsert(self, vector_id: str, embedding: List[float], metadata: Dict[str, Any]) -> None:
        self.collection.upsert(
            ids=[vector_id],
            embeddings=[embedding],
            metadatas=[metadata]
        )

    def similarity_search(self, query_embedding: List[float], limit: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> List[VectorSearchResult]:
        # query() in chroma returns ids, embeddings, metadatas, distances
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": limit
        }
        if filter_metadata:
            kwargs["where"] = filter_metadata
            
        results = self.collection.query(**kwargs)
        
        parsed_results = []
        if results and results["ids"] and len(results["ids"]) > 0:
            # We only queried one embedding, so we take index 0
            ids = results["ids"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0]*len(ids)
            
            for i in range(len(ids)):
                # Chroma returns distance. If using cosine, distance = 1 - cosine_similarity.
                # Lower distance is better.
                parsed_results.append(VectorSearchResult(
                    id=ids[i],
                    score=distances[i], 
                    metadata=metadatas[i]
                ))
                
        return parsed_results

    def delete(self, vector_id: str) -> None:
        self.collection.delete(ids=[vector_id])
