import os
import time
from app.interfaces.llm_client import LLMClient
from typing import Dict, Any

class GoogleADKAdapter(LLMClient):
    def __init__(self, model_name: str = "gemini-1.5-pro"):
        self.model_name = model_name
        self.last_metrics = {}
        
    def generate(self, prompt: str, system_context: str, parameters: Dict[str, Any]) -> str:
        start_time = time.time()
        
        # In a real environment, we would use the google-genai SDK here.
        # For Demo 2 determinism and given missing API keys, we return a hardcoded valid FastAPI response.
        
        response_text = """
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Todo(BaseModel):
    id: int
    title: str

todos = []

@app.get("/todos")
def get_todos():
    return todos

@app.post("/todos")
def create_todo(todo: Todo):
    todos.append(todo)
    return todo

# test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_and_get_todo():
    response = client.post("/todos", json={"id": 1, "title": "Buy milk"})
    assert response.status_code == 200
    assert response.json()["title"] == "Buy milk"
    
    response2 = client.get("/todos")
    assert len(response2.json()) == 1
    
# requirements.txt
fastapi==0.110.0
pytest==8.1.1
httpx==0.27.0
uvicorn==0.29.0
"""
        time.sleep(1) # simulate latency
        latency = (time.time() - start_time) * 1000
        
        self.last_metrics = {
            "tokens_used": len(prompt) // 4 + len(response_text) // 4,
            "latency_ms": latency,
            "model": self.model_name
        }
        
        return response_text
        
    def get_last_metrics(self) -> Dict[str, Any]:
        return self.last_metrics
