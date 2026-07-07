from typing import Protocol, List

class EmbeddingClient(Protocol):
    def embed_text(self, text: str) -> List[float]:
        ...

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        ...
