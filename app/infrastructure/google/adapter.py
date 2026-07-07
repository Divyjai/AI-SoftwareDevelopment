import time
import os
import google.generativeai as genai
from app.domain.models.llm import PromptRequest, LLMResponse
from typing import AsyncIterator
from app.interfaces.llm_client import LLMClient

class GoogleAdapter(LLMClient):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)

    def generate(self, request: PromptRequest) -> LLMResponse:
        start_time = time.time()
        
        generation_config = {
            "temperature": request.model_config.temperature,
            "max_output_tokens": request.model_config.max_tokens,
            "response_mime_type": "application/json"
        }
        
        model = genai.GenerativeModel(
            model_name=request.model_config.model,
            system_instruction=request.system_prompt
        )
        
        response = model.generate_content(
            request.compiled_prompt,
            generation_config=generation_config
        )
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        # Basic token counting (if available in this version)
        try:
            prompt_tokens = response.usage_metadata.prompt_token_count
            completion_tokens = response.usage_metadata.candidates_token_count
            total_tokens = response.usage_metadata.total_token_count
        except AttributeError:
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0
            
        try:
            # handle enum finish_reason
            finish_reason = str(response.candidates[0].finish_reason) if response.candidates else "UNKNOWN"
        except (AttributeError, IndexError):
            finish_reason = "UNKNOWN"

        return LLMResponse(
            generated_text=response.text,
            token_usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            },
            finish_reason=finish_reason,
            model_identifier=request.model_config.model,
            latency_ms=latency_ms,
            raw_provider_metadata={}
        )

    async def stream(self, request: PromptRequest) -> AsyncIterator[str]:
        import asyncio
        generation_config = {
            "temperature": request.model_config.temperature,
            "max_output_tokens": request.model_config.max_tokens,
            "response_mime_type": "application/json"
        }
        
        model = genai.GenerativeModel(
            model_name=request.model_config.model,
            system_instruction=request.system_prompt
        )
        
        response = await model.generate_content_async(
            request.compiled_prompt,
            generation_config=generation_config,
            stream=True
        )
        
        async for chunk in response:
            yield chunk.text
