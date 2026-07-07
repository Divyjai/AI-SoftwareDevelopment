from abc import ABC, abstractmethod
from typing import List, Dict, Any

class RetrievalHistoryRepository(ABC):
    @abstractmethod
    def log_retrieval(self, query: str, execution_id: str, returned_ids: List[str], scores: List[float], metadata: Dict[str, Any]):
        pass
        
    @abstractmethod
    def get_history(self, execution_id: str) -> List[Dict[str, Any]]:
        pass
