import sqlite3
import json
import time
import uuid
from typing import List, Dict, Any
from app.interfaces.retrieval_history_repository import RetrievalHistoryRepository

class SQLiteRetrievalHistoryRepository(RetrievalHistoryRepository):
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

    def log_retrieval(self, query: str, execution_id: str, returned_ids: List[str], scores: List[float], metadata: Dict[str, Any]):
        # Construct chosen memory ids (which currently are the returned ones)
        # Store scores in metadata
        meta = metadata.copy()
        meta["scores"] = scores
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO retrieval_history (
                    id, query, execution_id, top_k_retrieved_ids, chosen_memory_ids, prompt_injected, timestamp, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"ret-{uuid.uuid4().hex[:8]}",
                query,
                execution_id,
                json.dumps(returned_ids),
                json.dumps(returned_ids),
                "", # No prompt injected logged directly here anymore, we log metadata
                time.time(),
                json.dumps(meta)
            ))

    def get_history(self, execution_id: str) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM retrieval_history WHERE execution_id = ? ORDER BY timestamp DESC", 
                (execution_id,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
