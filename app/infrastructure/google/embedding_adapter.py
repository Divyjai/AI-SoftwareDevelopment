from typing import List
import google.generativeai as genai
from app.interfaces.embedding_client import EmbeddingClient

class GoogleEmbeddingAdapter(EmbeddingClient):
    def __init__(self, api_key: str):
        self.api_key = api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)

    def embed_text(self, text: str) -> List[float]:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text
        )
        return result['embedding']

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=texts
        )
        return result['embedding']
