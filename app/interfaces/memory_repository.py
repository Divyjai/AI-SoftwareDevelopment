from typing import Protocol, List, Dict, Any, Optional
from app.domain.memory.models import MemoryRecord, MemoryType

class MemoryRepository(Protocol):
    def save(self, record: MemoryRecord) -> None:
        ...

    def update(self, record: MemoryRecord) -> None:
        ...

    def get(self, memory_id: str) -> Optional[MemoryRecord]:
        ...

    def delete(self, memory_id: str) -> None:
        ...

    def filter(self, 
               memory_type: Optional[MemoryType] = None, 
               workflow_id: Optional[str] = None,
               task_id: Optional[str] = None,
               tags: Optional[List[str]] = None,
               limit: int = 10) -> List[MemoryRecord]:
        ...
