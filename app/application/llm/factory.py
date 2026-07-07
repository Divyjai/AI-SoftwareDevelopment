import os
from app.interfaces.llm_provider import LLMProvider
from app.application.llm.registry import ProviderRegistry
from app.infrastructure.google.provider import GoogleProvider
from app.infrastructure.ollama.provider import OllamaProvider

# Register default providers
ProviderRegistry.register("google", GoogleProvider)
ProviderRegistry.register("ollama", OllamaProvider)

class LLMFactory:
    @staticmethod
    def create() -> LLMProvider:
        provider_name = os.environ.get("LLM_PROVIDER", "google").lower()
        provider_class = ProviderRegistry.get(provider_name)
        return provider_class()
