from typing import Protocol, AsyncIterator
from app.domain.models.llm import PromptRequest, LLMResponse

class LLMClient(Protocol):
    def generate(self, request: PromptRequest) -> LLMResponse:
        ...

    async def stream(self, request: PromptRequest) -> AsyncIterator[str]:
        ...
