import sqlite3
import json
from typing import List, Optional
from app.domain.memory.models import MemoryRecord, MemoryType, MemorySource
from app.interfaces.memory_repository import MemoryRepository

class SQLiteMemoryRepository(MemoryRepository):
    def __init__(self, db_path: str = "demo2_artifacts.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    memory_type TEXT,
                    workflow_id TEXT,
                    task_id TEXT,
                    agent_id TEXT,
                    summary TEXT,
                    created_at REAL,
                    updated_at REAL,
                    artifact_ids TEXT,
                    execution_id TEXT,
                    embedding_id TEXT,
                    importance REAL,
                    tags TEXT,
                    metadata TEXT,
                    version INTEGER,
                    parent_memory_id TEXT,
                    supersedes_id TEXT,
                    is_latest BOOLEAN,
                    source TEXT
                )
            """)

    def save(self, record: MemoryRecord) -> None:
        with sqlite3.connect(self.db_path) as conn:
            # If this supersedes an older record, update the older record's is_latest to False
            if record.supersedes_id:
                conn.execute("UPDATE memories SET is_latest = 0 WHERE id = ?", (record.supersedes_id,))
                
            conn.execute("""
                INSERT INTO memories (
                    id, memory_type, workflow_id, task_id, agent_id, summary, 
                    created_at, updated_at, artifact_ids, execution_id, 
                    embedding_id, importance, tags, metadata,
                    version, parent_memory_id, supersedes_id, is_latest, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.id,
                record.memory_type.value,
                record.workflow_id,
                record.task_id,
                record.agent_id,
                record.summary,
                record.created_at,
                record.updated_at,
                json.dumps(record.artifact_ids),
                record.execution_id,
                record.embedding_id,
                record.importance,
                json.dumps(record.tags),
                json.dumps(record.metadata),
                record.version,
                record.parent_memory_id,
                record.supersedes_id,
                1 if record.is_latest else 0,
                record.source.value
            ))

    def update(self, record: MemoryRecord) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE memories SET
                    memory_type=?, workflow_id=?, task_id=?, agent_id=?, summary=?,
                    updated_at=?, artifact_ids=?, execution_id=?, embedding_id=?,
                    importance=?, tags=?, metadata=?,
                    version=?, parent_memory_id=?, supersedes_id=?, is_latest=?, source=?
                WHERE id=?
            """, (
                record.memory_type.value,
                record.workflow_id,
                record.task_id,
                record.agent_id,
                record.summary,
                record.updated_at,
                json.dumps(record.artifact_ids),
                record.execution_id,
                record.embedding_id,
                record.importance,
                json.dumps(record.tags),
                json.dumps(record.metadata),
                record.version,
                record.parent_memory_id,
                record.supersedes_id,
                1 if record.is_latest else 0,
                record.source.value,
                record.id
            ))

    def get(self, memory_id: str) -> Optional[MemoryRecord]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM memories WHERE id=?", (memory_id,)).fetchone()
            if not row:
                return None
            return self._row_to_record(row)

    def delete(self, memory_id: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM memories WHERE id=?", (memory_id,))

    def filter(self, 
               memory_type: Optional[MemoryType] = None, 
               workflow_id: Optional[str] = None,
               task_id: Optional[str] = None,
               tags: Optional[List[str]] = None,
               limit: int = 10,
               only_latest: bool = True) -> List[MemoryRecord]:
        query = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if only_latest:
            query += " AND is_latest = 1"
            
        if memory_type:
            query += " AND memory_type=?"
            params.append(memory_type.value)
        if workflow_id:
            query += " AND workflow_id=?"
            params.append(workflow_id)
        if task_id:
            query += " AND task_id=?"
            params.append(task_id)
            
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        records = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
            for row in rows:
                record = self._row_to_record(row)
                if tags:
                    if not all(tag in record.tags for tag in tags):
                        continue
                records.append(record)
        return records

    def _row_to_record(self, row) -> MemoryRecord:
        row_keys = row.keys()
        return MemoryRecord(
            id=row["id"],
            memory_type=MemoryType(row["memory_type"]),
            workflow_id=row["workflow_id"],
            task_id=row["task_id"],
            agent_id=row["agent_id"],
            summary=row["summary"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            artifact_ids=json.loads(row["artifact_ids"]),
            execution_id=row["execution_id"],
            embedding_id=row["embedding_id"],
            importance=row["importance"],
            tags=json.loads(row["tags"]),
            metadata=json.loads(row["metadata"]),
            version=row["version"] if "version" in row_keys else 1,
            parent_memory_id=row["parent_memory_id"] if "parent_memory_id" in row_keys else None,
            supersedes_id=row["supersedes_id"] if "supersedes_id" in row_keys else None,
            is_latest=bool(row["is_latest"]) if "is_latest" in row_keys else True,
            source=MemorySource(row["source"] if "source" in row_keys and row["source"] else "USER")
        )
