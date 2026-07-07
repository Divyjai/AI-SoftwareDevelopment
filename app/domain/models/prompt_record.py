from dataclasses import dataclass

@dataclass
class PromptRecord:
    prompt_id: str
    compiled_prompt_text: str
    system_prompt_version: str
    model_name: str
    temperature: float
    max_tokens: int
    tokens_used: int
    latency_ms: float
    prompt_template_version: str = "1.0.0"
    compiled_prompt_checksum: str = ""
