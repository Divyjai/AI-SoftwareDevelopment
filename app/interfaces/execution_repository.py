from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ExecutionRepository(ABC):
    @abstractmethod
    def get_recent_executions(self, limit: int = 10) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def save_execution(self, execution_data: Dict[str, Any]):
        pass
