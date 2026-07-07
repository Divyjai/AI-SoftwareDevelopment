from pathlib import Path
from app.application.agents.database_agent import DatabasePlanner, DatabaseExecutionAgent
from app.domain.models.database import DatabaseConfig, DatabaseConnection, SchemaSnapshot
from app.domain.models.database_graph import DatabaseGraph, DatabaseGraphVersion
from datetime import datetime
import uuid

class DatabaseEngine:
    def __init__(self, workspace_path: str, execution_engine, repair_engine, memory_service, project_state):
        self.workspace_path = Path(workspace_path)
        self.execution_engine = execution_engine
        self.repair_engine = repair_engine
        self.memory_service = memory_service
        self.project_state = project_state
        
        self.planner = DatabasePlanner()
        self.execution_agent = DatabaseExecutionAgent(execution_engine)

    def run_database_cycle(self, context) -> bool:
        db_config = DatabaseConfig(
            connection=DatabaseConnection(uri="sqlite:///test.db", dialect="sqlite"),
            pool_size=1
        )
        
        # 1. Plan Phase
        plan_output = self.planner.run(context, db_config)
        
        # 2. Execution Phase
        # Wrapped in a retry loop to hook into RepairEngine if Migration Fails
        max_attempts = 3
        artifacts = []
        for attempt in range(max_attempts):
            try:
                artifacts = self.execution_agent.run(plan_output, db_config)
                break
            except Exception as e:
                # If failure, we would call DatabaseFailureAnalyzer and then RepairEngine
                # For demo purposes, we break or simulate repair
                self.repair_engine.run_repair(
                    execution_id=f"db-exec-{attempt}",
                    raw_failure_output=str(e)
                )
                
        # 3. Write Artifacts to Filesystem
        for artifact in artifacts:
            file_path = self.workspace_path / artifact.metadata["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(artifact.content)
                
        # 4. Versioning and Observability (Snapshotting)
        snapshot = SchemaSnapshot(
            snapshot_id=str(uuid.uuid4()),
            schema_version="v1",
            created_at=datetime.utcnow(),
            checksum="mock_checksum",
            database_schema=plan_output["desired_schema"],
            execution_id=f"exec-{uuid.uuid4()}"
        )
        
        graph_version = DatabaseGraphVersion(
            version="v1",
            parent_version="v0",
            schema_snapshot=snapshot,
            created_at=datetime.utcnow(),
            graph=DatabaseGraph()
        )
        
        # Normally we'd save snapshot and graph_version to memory
        return True
