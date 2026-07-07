import sqlite3
import json
import uuid
from typing import List
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class RetrievalLog:
    id: str
    query: str
    execution_id: str
    top_k_retrieved_ids: List[str]
    chosen_memory_ids: List[str]
    prompt_injected: str
    timestamp: float

    @classmethod
    def create(cls, query: str, execution_id: str, top_k_retrieved_ids: List[str], chosen_memory_ids: List[str], prompt_injected: str) -> "RetrievalLog":
        return cls(
            id=f"ret-{uuid.uuid4().hex[:8]}",
            query=query,
            execution_id=execution_id,
            top_k_retrieved_ids=top_k_retrieved_ids,
            chosen_memory_ids=chosen_memory_ids,
            prompt_injected=prompt_injected,
            timestamp=datetime.utcnow().timestamp()
        )

class RetrievalHistory:
    def __init__(self, db_path: str = "demo2_artifacts.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS retrieval_history (
                    id TEXT PRIMARY KEY,
                    query TEXT,
                    execution_id TEXT,
                    top_k_retrieved_ids TEXT,
                    chosen_memory_ids TEXT,
                    prompt_injected TEXT,
                    timestamp REAL,
                    metadata TEXT
                )
            """)

    def log(self, record: RetrievalLog) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO retrieval_history (
                    id, query, execution_id, top_k_retrieved_ids, chosen_memory_ids, prompt_injected, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                record.id,
                record.query,
                record.execution_id,
                json.dumps(record.top_k_retrieved_ids),
                json.dumps(record.chosen_memory_ids),
                record.prompt_injected,
                record.timestamp
            ))
