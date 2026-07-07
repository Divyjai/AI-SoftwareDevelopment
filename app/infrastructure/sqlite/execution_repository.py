import sqlite3
import json
from typing import List, Dict, Any
from app.interfaces.execution_repository import ExecutionRepository

class SQLiteExecutionRepository(ExecutionRepository):
    def __init__(self, db_path: str = "demo2_artifacts.db"):
        self.db_path = db_path

    def get_recent_executions(self, limit: int = 10) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            # Let's ensure the table is created if it hasn't been by SQLiteArtifactRepository yet
            conn.execute('''CREATE TABLE IF NOT EXISTS execution_results
                             (execution_id TEXT PRIMARY KEY, start_time REAL, end_time REAL, duration REAL,
                              exit_code INTEGER, status TEXT, dependencies_installed INTEGER,
                              workspace_path TEXT, stdout TEXT, stderr TEXT, correlation_id TEXT)''')
            
            cursor = conn.execute(
                "SELECT * FROM execution_results ORDER BY start_time DESC LIMIT ?", 
                (limit,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
    def save_execution(self, execution_data: Dict[str, Any]):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS execution_results
                             (execution_id TEXT PRIMARY KEY, start_time REAL, end_time REAL, duration REAL,
                              exit_code INTEGER, status TEXT, dependencies_installed INTEGER,
                              workspace_path TEXT, stdout TEXT, stderr TEXT, correlation_id TEXT)''')
            conn.execute("""
                INSERT OR REPLACE INTO execution_results (
                    execution_id, start_time, end_time, duration, exit_code, 
                    status, dependencies_installed, workspace_path, stdout, stderr, correlation_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution_data.get("execution_id"),
                execution_data.get("start_time"),
                execution_data.get("end_time"),
                execution_data.get("duration"),
                execution_data.get("exit_code"),
                execution_data.get("status"),
                json.dumps(execution_data.get("dependencies_installed", [])),
                execution_data.get("workspace_path"),
                execution_data.get("stdout"),
                execution_data.get("stderr"),
                execution_data.get("correlation_id")
            ))
