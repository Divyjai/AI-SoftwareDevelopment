import os
import pytest
from app.application.llm.factory import LLMFactory
from app.domain.models.llm import PromptRequest, ModelConfig

# Note: this test requires Ollama running locally at localhost:11434 with qwen3:4b
@pytest.mark.asyncio
async def test_ollama_provider_integration():
    # Force the factory to use ollama
    os.environ["LLM_PROVIDER"] = "ollama"
    
    provider = LLMFactory.create()
    assert provider.name == "ollama"
    
    # Check health
    health = provider.health_check()
    
    if not health.healthy:
        pytest.skip(f"Ollama is not healthy or running locally: {health.error}")
        
    client = provider.get_client()
    
    request = PromptRequest(
        compiled_prompt="Hello, say 'test passed' exactly.",
        model_config=ModelConfig(
            model=health.model,
            temperature=0.0,
            max_tokens=10
        )
    )
    
    response = client.generate(request)
    
    assert response is not None
    assert "test passed" in response.generated_text.lower()
    
    # Test streaming capability if supported
    if provider.capabilities.supports_streaming:
        chunks = []
        async for chunk in client.stream(request):
            chunks.append(chunk)
            
        streamed_text = "".join(chunks)
        assert len(streamed_text) > 0
