import ollama
from app.infrastructure.ollama.config import OllamaConfig

class OllamaClient:
    def __init__(self, config: OllamaConfig):
        self.config = config
        self._client = ollama.Client(host=config.host)

    def get_client(self) -> ollama.Client:
        return self._client
