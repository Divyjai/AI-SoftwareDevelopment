import sqlite3
from pathlib import Path
from typing import List, Dict, Any

class AcceptanceRepository:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def _execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def _execute_single(self, query: str, params: tuple = ()) -> Dict[str, Any]:
        results = self._execute_query(query, params)
        return results[0] if results else None

    def get_execution(self, execution_id: str) -> Dict[str, Any]:
        return self._execute_single("SELECT * FROM execution_results WHERE execution_id = ?", (execution_id,))

    def get_latest_execution_id(self) -> str:
        row = self._execute_single("SELECT execution_id FROM execution_results ORDER BY start_time DESC LIMIT 1")
        return row['execution_id'] if row else None

    def get_artifacts_for_execution(self, execution_id: str) -> List[Dict[str, Any]]:
        return self._execute_query("SELECT * FROM artifacts WHERE produced_by_task = ?", (execution_id,))

    def get_events_for_execution(self, execution_id: str) -> List[Dict[str, Any]]:
        return self._execute_query("SELECT * FROM events WHERE execution_id = ? ORDER BY timestamp ASC", (execution_id,))

    def get_manifest(self, execution_id: str) -> Dict[str, Any]:
        return self._execute_single("SELECT * FROM workspace_manifests WHERE execution_id = ?", (execution_id,))

    def get_prompts_for_execution(self, execution_id: str) -> List[Dict[str, Any]]:
        return self._execute_query("SELECT * FROM prompt_records WHERE execution_id = ?", (execution_id,))

class Demo2AcceptanceContext:
    def __init__(self, db_path: Path, execution_id: str = None):
        self.db_path = db_path
        self.repo = AcceptanceRepository(db_path)
        
        self.execution_id = execution_id or self.repo.get_latest_execution_id()
        if not self.execution_id:
            raise ValueError("No Demo 2 execution found in database.")
            
    @property
    def execution(self) -> Dict[str, Any]:
        if not hasattr(self, '_execution'):
            self._execution = self.repo.get_execution(self.execution_id)
        return self._execution
        
    @property
    def artifacts(self) -> List[Dict[str, Any]]:
        if not hasattr(self, '_artifacts'):
            self._artifacts = self.repo.get_artifacts_for_execution(self.execution_id)
        return self._artifacts
        
    @property
    def events(self) -> List[Dict[str, Any]]:
        if not hasattr(self, '_events'):
            self._events = self.repo.get_events_for_execution(self.execution_id)
        return self._events
        
    @property
    def manifest(self) -> Dict[str, Any]:
        if not hasattr(self, '_manifest'):
            self._manifest = self.repo.get_manifest(self.execution_id)
        return self._manifest
        
    @property
    def prompts(self) -> List[Dict[str, Any]]:
        if not hasattr(self, '_prompts'):
            self._prompts = self.repo.get_prompts_for_execution(self.execution_id)
        return self._prompts

