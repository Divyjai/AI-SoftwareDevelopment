from typing import Dict, Type
from app.interfaces.llm_provider import LLMProvider

class ProviderRegistry:
    _registry: Dict[str, Type[LLMProvider]] = {}

    @classmethod
    def register(cls, name: str, provider_class: Type[LLMProvider]):
        cls._registry[name] = provider_class

    @classmethod
    def get(cls, name: str) -> Type[LLMProvider]:
        if name not in cls._registry:
            raise ValueError(f"Provider '{name}' not found in registry.")
        return cls._registry[name]
