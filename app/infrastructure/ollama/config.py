import os
from dataclasses import dataclass

@dataclass
class OllamaConfig:
    host: str = "http://localhost:11434"
    model: str = "qwen3:4b"
    embedding_model: str = "nomic-embed-text"
    temperature: float = 0.7
    max_tokens: int = 8192
    top_p: float = 1.0

    @classmethod
    def from_env(cls) -> "OllamaConfig":
        return cls(
            host=os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
            model=os.environ.get("OLLAMA_MODEL", "qwen3:4b"),
            embedding_model=os.environ.get("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"),
            temperature=float(os.environ.get("OLLAMA_TEMPERATURE", 0.7)),
            max_tokens=int(os.environ.get("OLLAMA_MAX_TOKENS", 8192)),
            top_p=float(os.environ.get("OLLAMA_TOP_P", 1.0))
        )
