from typing import List, Dict, Any
from app.domain.memory.models import MemoryRecord
from app.domain.models.artifact import Artifact
from app.domain.models.task import Task

class KnowledgeRanker:
    def rank_memories(self, candidates: List[MemoryRecord], top_k: int = 10) -> List[MemoryRecord]:
        # Sort by importance, score, or other heuristics. 
        # For now, memory service already ranks via retrieve(), but we can do further trimming
        # Just taking the first top_k
        return candidates[:top_k]

    def rank_artifacts(self, candidates: List[Artifact], task: Task, top_k: int = 5) -> List[Artifact]:
        # In a real scenario, this might use semantic search on artifact contents vs task
        # For now, just return top_k
        return candidates[:top_k]

    def rank_executions(self, candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        # Usually sort by recency or failure
        # Executions are already sorted by time descending usually
        return candidates[:top_k]
