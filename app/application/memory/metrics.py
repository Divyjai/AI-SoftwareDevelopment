from dataclasses import dataclass

@dataclass
class MemoryStats:
    total_records: int = 0
    total_embeddings: int = 0
    total_embedding_time: float = 0.0
    total_retrieval_time: float = 0.0
    total_retrievals: int = 0
    cache_hits: int = 0
    
    @property
    def average_embedding_time(self) -> float:
        if self.total_embeddings == 0:
            return 0.0
        return self.total_embedding_time / self.total_embeddings

    @property
    def average_retrieval_latency(self) -> float:
        if self.total_retrievals == 0:
            return 0.0
        return self.total_retrieval_time / self.total_retrievals

class MemoryMetrics:
    def __init__(self):
        self.stats = MemoryStats()

    def record_embedded(self, duration: float, cached: bool = False):
        if cached:
            self.stats.cache_hits += 1
        else:
            self.stats.total_embeddings += 1
            self.stats.total_embedding_time += duration

    def record_retrieval(self, duration: float):
        self.stats.total_retrievals += 1
        self.stats.total_retrieval_time += duration

    def record_saved(self):
        self.stats.total_records += 1

    def get_stats(self) -> MemoryStats:
        return self.stats
