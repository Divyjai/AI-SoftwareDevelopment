import time
from app.interfaces.llm_provider import LLMProvider, ProviderCapabilities, HealthStatus
from app.interfaces.llm_client import LLMClient
from app.infrastructure.ollama.client import OllamaClient
from app.infrastructure.ollama.config import OllamaConfig
from app.infrastructure.ollama.adapter import OllamaAdapter

class OllamaProvider(LLMProvider):
    def __init__(self):
        self._config = OllamaConfig.from_env()
        self._client = OllamaClient(self._config)

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_json=True,
            supports_streaming=True,
            supports_tools=True,
            supports_embeddings=True,
            supports_images=True
        )

    def get_client(self) -> LLMClient:
        return OllamaAdapter(self._client)

    def health_check(self) -> HealthStatus:
        start_time = time.time()
        try:
            # list() internally calls /api/tags
            self._client.get_client().list()
            latency_ms = int((time.time() - start_time) * 1000)
            return HealthStatus(
                healthy=True,
                latency_ms=latency_ms,
                model=self._config.model,
                provider="ollama",
                error=None
            )
        except Exception as e:
            return HealthStatus(
                healthy=False,
                latency_ms=0,
                model=self._config.model,
                provider="ollama",
                error=str(e)
            )
