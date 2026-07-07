from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class ModelConfig:
    model: str
    temperature: float = 0.0
    max_tokens: Optional[int] = 8192
    top_p: Optional[float] = None
    seed: Optional[int] = None

@dataclass
class PromptRequest:
    compiled_prompt: str
    model_config: ModelConfig
    system_prompt: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LLMResponse:
    generated_text: str
    token_usage: Dict[str, int]
    finish_reason: str
    model_identifier: str
    latency_ms: float
    raw_provider_metadata: Dict[str, Any] = field(default_factory=dict)
