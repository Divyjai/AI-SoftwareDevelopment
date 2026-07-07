import os
import time
from app.interfaces.llm_provider import LLMProvider, ProviderCapabilities, HealthStatus
from app.interfaces.llm_client import LLMClient
from app.infrastructure.google.adapter import GoogleAdapter

class GoogleProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.model_name = os.environ.get("GOOGLE_MODEL", "gemini-1.5-pro")

    @property
    def name(self) -> str:
        return "google"

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
        return GoogleAdapter(self.api_key)

    def health_check(self) -> HealthStatus:
        # A simple check could be just verifying api key is present,
        # or we could make a lightweight API call.
        if self.api_key:
            return HealthStatus(
                healthy=True,
                latency_ms=0,
                model=self.model_name,
                provider="google",
                error=None
            )
        return HealthStatus(
            healthy=False,
            latency_ms=0,
            model=self.model_name,
            provider="google",
            error="API key not found"
        )
