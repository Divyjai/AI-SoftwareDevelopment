import sqlite3
import json
from app.interfaces.artifact_repository import ArtifactRepository
from app.domain.models.artifact import Artifact, ArtifactState

class SQLiteArtifactRepository(ArtifactRepository):
    def __init__(self, db_path: str = "artifacts.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS artifacts
                             (id TEXT PRIMARY KEY, version TEXT, owner TEXT, status TEXT, 
                              content TEXT, produced_by_task TEXT, depends_on TEXT, depended_by TEXT,
                              artifact_type TEXT, checksum TEXT)''')
                              
        self.conn.execute('''CREATE TABLE IF NOT EXISTS execution_results
                             (execution_id TEXT PRIMARY KEY, start_time REAL, end_time REAL, duration REAL,
                              exit_code INTEGER, status TEXT, dependencies_installed INTEGER,
                              workspace_path TEXT, stdout TEXT, stderr TEXT, correlation_id TEXT)''')
                              
        self.conn.execute('''CREATE TABLE IF NOT EXISTS events
                             (id TEXT PRIMARY KEY, event_type TEXT, timestamp REAL, 
                              execution_id TEXT, correlation_id TEXT, details TEXT)''')
                              
        self.conn.execute('''CREATE TABLE IF NOT EXISTS workspace_manifests
                             (execution_id TEXT PRIMARY KEY, workspace_path TEXT, files TEXT)''')
                              
        self.conn.execute('''CREATE TABLE IF NOT EXISTS prompt_records
                             (prompt_id TEXT PRIMARY KEY, execution_id TEXT, compiled_prompt_text TEXT,
                              system_prompt_version TEXT, model_name TEXT, temperature REAL, max_tokens INTEGER,
                              prompt_tokens INTEGER, completion_tokens INTEGER, latency_ms REAL,
                              prompt_template_version TEXT, compiled_prompt_checksum TEXT)''')
        self.conn.commit()
        
    def save(self, artifact: Artifact):
        content_str = json.dumps(artifact.content) if isinstance(artifact.content, dict) else str(artifact.content)
        depends_on = json.dumps(artifact.depends_on)
        depended_by = json.dumps(artifact.depended_by)
        artifact_type = getattr(artifact, 'artifact_type', 'UNKNOWN')
        checksum = getattr(artifact, 'checksum', None)
        
        # In python standard library hashlib can be used if checksum is not generated
        if not checksum and content_str:
            import hashlib
            checksum = hashlib.sha256(content_str.encode('utf-8')).hexdigest()
            
        self.conn.execute("INSERT OR REPLACE INTO artifacts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (artifact.id, artifact.version, artifact.owner, artifact.status.value, 
                           content_str, artifact.produced_by_task, depends_on, depended_by, artifact_type, checksum))
        self.conn.commit()
        
    def get(self, artifact_id: str) -> Artifact:
        cursor = self.conn.execute("SELECT * FROM artifacts WHERE id=?", (artifact_id,))
        row = cursor.fetchone()
        if not row: return None
        art = Artifact(
            id=row[0], version=row[1], owner=row[2], status=ArtifactState(row[3]),
            content=row[4], produced_by_task=row[5], 
            depends_on=json.loads(row[6]), depended_by=json.loads(row[7])
        )
        art.artifact_type = row[8]
        art.checksum = row[9]
        return art

    def get_recent_artifacts(self, limit: int = 10) -> list[Artifact]:
        cursor = self.conn.execute("SELECT * FROM artifacts LIMIT ?", (limit,))
        artifacts = []
        for row in cursor.fetchall():
            art = Artifact(
                id=row[0], version=row[1], owner=row[2], status=ArtifactState(row[3]),
                content=row[4], produced_by_task=row[5], 
                depends_on=json.loads(row[6]), depended_by=json.loads(row[7])
            )
            art.artifact_type = row[8]
            art.checksum = row[9]
            artifacts.append(art)
        return artifacts

    def save_execution(self, exec_data: dict):
        self.conn.execute("INSERT OR REPLACE INTO execution_results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (exec_data['execution_id'], exec_data.get('start_time'), exec_data.get('end_time'),
                           exec_data.get('duration'), exec_data.get('exit_code'), exec_data.get('status'),
                           exec_data.get('dependencies_installed'), exec_data.get('workspace_path'),
                           exec_data.get('stdout'), exec_data.get('stderr'), exec_data.get('correlation_id')))
        self.conn.commit()

    def save_event(self, event_data: dict):
        self.conn.execute("INSERT OR REPLACE INTO events VALUES (?, ?, ?, ?, ?, ?)",
                          (event_data['id'], event_data['event_type'], event_data['timestamp'],
                           event_data.get('execution_id'), event_data.get('correlation_id'),
                           json.dumps(event_data.get('details', {}))))
        self.conn.commit()

    def save_manifest(self, manifest_data: dict):
        self.conn.execute("INSERT OR REPLACE INTO workspace_manifests VALUES (?, ?, ?)",
                          (manifest_data['execution_id'], manifest_data['workspace_path'],
                           json.dumps(manifest_data.get('files', []))))
        self.conn.commit()

    def save_prompt_record(self, prompt_data: dict):
        self.conn.execute("INSERT OR REPLACE INTO prompt_records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (prompt_data['prompt_id'], prompt_data.get('execution_id'), 
                           prompt_data.get('compiled_prompt_text'), prompt_data.get('system_prompt_version'),
                           prompt_data.get('model_name'), prompt_data.get('temperature'),
                           prompt_data.get('max_tokens'), prompt_data.get('prompt_tokens'),
                           prompt_data.get('completion_tokens'), prompt_data.get('latency_ms'),
                           prompt_data.get('prompt_template_version'), prompt_data.get('compiled_prompt_checksum')))
        self.conn.commit()
