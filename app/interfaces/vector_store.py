from typing import Protocol, List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class VectorSearchResult:
    id: str
    score: float
    metadata: Dict[str, Any]

class VectorStore(Protocol):
    def upsert(self, vector_id: str, embedding: List[float], metadata: Dict[str, Any]) -> None:
        ...

    def similarity_search(self, query_embedding: List[float], limit: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> List[VectorSearchResult]:
        ...

    def delete(self, vector_id: str) -> None:
        ...
