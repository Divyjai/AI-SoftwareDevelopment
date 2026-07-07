from typing import Dict, Any
from app.domain.models.llm import PromptRequest

def map_request(request: PromptRequest) -> Dict[str, Any]:
    messages = []
    
    if request.system_prompt:
        messages.append({
            "role": "system",
            "content": request.system_prompt
        })
        
    messages.append({
        "role": "user",
        "content": request.compiled_prompt
    })
    
    # Ollama uses options to specify temperature, etc.
    options = {}
    if request.model_config.temperature is not None:
        options["temperature"] = request.model_config.temperature
    if request.model_config.max_tokens is not None:
        options["num_predict"] = request.model_config.max_tokens
    if request.model_config.top_p is not None:
        options["top_p"] = request.model_config.top_p
    if request.model_config.seed is not None:
        options["seed"] = request.model_config.seed
        
    payload = {
        "model": request.model_config.model,
        "messages": messages,
        "stream": False
    }
    
    if options:
        payload["options"] = options
        
    return payload
