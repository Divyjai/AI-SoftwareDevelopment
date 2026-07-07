from typing import Dict, Any
from app.domain.models.llm import LLMResponse

def map_response(raw_response: Dict[str, Any], latency_ms: float, model: str) -> LLMResponse:
    message = raw_response.get("message", {})
    content = message.get("content", "")
    
    # Ollama returns eval_count, prompt_eval_count
    prompt_tokens = raw_response.get("prompt_eval_count", 0)
    completion_tokens = raw_response.get("eval_count", 0)
    total_tokens = prompt_tokens + completion_tokens
    
    done = raw_response.get("done", True)
    finish_reason = "stop" if done else "unknown"
    
    return LLMResponse(
        generated_text=content,
        token_usage={
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        },
        finish_reason=finish_reason,
        model_identifier=raw_response.get("model", model),
        latency_ms=latency_ms,
        raw_provider_metadata=raw_response
    )
