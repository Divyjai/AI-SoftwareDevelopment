from typing import Protocol, Optional
from dataclasses import dataclass
from app.interfaces.llm_client import LLMClient

@dataclass
class ProviderCapabilities:
    supports_json: bool
    supports_streaming: bool
    supports_tools: bool
    supports_embeddings: bool
    supports_images: bool

@dataclass
class HealthStatus:
    healthy: bool
    latency_ms: int
    model: str
    provider: str
    error: Optional[str] = None

class LLMProvider(Protocol):
    @property
    def name(self) -> str:
        ...

    @property
    def capabilities(self) -> ProviderCapabilities:
        ...

    def get_client(self) -> LLMClient:
        ...

    def health_check(self) -> HealthStatus:
        ...
