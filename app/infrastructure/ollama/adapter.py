import time
from typing import AsyncIterator
from app.interfaces.llm_client import LLMClient
from app.domain.models.llm import PromptRequest, LLMResponse
from app.infrastructure.ollama.client import OllamaClient
from app.infrastructure.ollama.request_mapper import map_request
from app.infrastructure.ollama.response_mapper import map_response

class OllamaAdapter(LLMClient):
    def __init__(self, ollama_client: OllamaClient):
        self._client = ollama_client.get_client()

    def generate(self, request: PromptRequest) -> LLMResponse:
        start_time = time.time()
        
        payload = map_request(request)
        payload["stream"] = False
        
        # Uses sync ollama client chat
        response = self._client.chat(**payload)
        
        latency_ms = (time.time() - start_time) * 1000
        
        return map_response(response, latency_ms, request.model_config.model)

    async def stream(self, request: PromptRequest) -> AsyncIterator[str]:
        # Implementation for streaming
        payload = map_request(request)
        payload["stream"] = True
        
        # For an AsyncIterator, we'd typically use AsyncClient, but since this protocol is async def stream()
        # and we use sync client, we can either use ollama.AsyncClient or wrap sync generator
        # Assuming we might want AsyncClient later, we'll yield chunks.
        # Note: if self._client is sync, .chat(stream=True) returns a generator, not async generator.
        # This is a placeholder for actual async streaming.
        for chunk in self._client.chat(**payload):
            if "message" in chunk and "content" in chunk["message"]:
                yield chunk["message"]["content"]
