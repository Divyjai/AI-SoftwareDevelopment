import sqlite3
import json
import hashlib
from typing import List, Optional

class SQLiteEmbeddingCache:
    def __init__(self, db_path: str = "demo2_artifacts.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS embedding_cache (
                    checksum TEXT PRIMARY KEY,
                    embedding TEXT
                )
            """)

    def _compute_checksum(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def get(self, text: str) -> Optional[List[float]]:
        checksum = self._compute_checksum(text)
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT embedding FROM embedding_cache WHERE checksum=?", (checksum,)).fetchone()
            if row:
                return json.loads(row[0])
        return None

    def set(self, text: str, embedding: List[float]) -> None:
        checksum = self._compute_checksum(text)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO embedding_cache (checksum, embedding) 
                VALUES (?, ?)
            """, (checksum, json.dumps(embedding)))
