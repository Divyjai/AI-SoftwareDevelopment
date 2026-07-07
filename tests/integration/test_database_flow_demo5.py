import os
import tempfile
from pathlib import Path
from app.application.database.engine import DatabaseEngine
from app.shared.state.project_state import ProjectState
from app.domain.models.agent_context import AgentContext
from app.domain.models.project import Task

class MockExecutionEngine:
    pass

class MockRepairEngine:
    def __init__(self):
        self.repaired = False
    
    def run_repair(self, execution_id: str, raw_failure_output: str):
        self.repaired = True

class MockMemoryService:
    pass

def test_database_flow_demo5():
    with tempfile.TemporaryDirectory() as temp_dir:
        state = ProjectState()
        repair_engine = MockRepairEngine()
        
        db_engine = DatabaseEngine(
            workspace_path=temp_dir,
            execution_engine=MockExecutionEngine(),
            repair_engine=repair_engine,
            memory_service=MockMemoryService(),
            project_state=state
        )
        
        class MockTask:
            def __init__(self, description):
                self.description = description
                
        class MockContext:
            def __init__(self, task):
                self.task = task
                
        # Context providing the Demo 5 prompt
        task_prompt = "Build a Multi-tenant Task Management Platform with Users, Organizations, Projects, Roles, Permissions, Tasks, Comments, Attachments, Notifications, Audit Logs, Tags, and Categories"
        context = MockContext(task=MockTask(description=task_prompt))
        
        # Execute the database lifecycle
        result = db_engine.run_database_cycle(context)
        
        assert result is True
        
        workspace = Path(temp_dir)
        models_file = workspace / "app" / "models.py"
        seed_file = workspace / "scripts" / "seed.py"
        
        assert models_file.exists(), "ORM models should be generated"
        assert seed_file.exists(), "Seed data should be generated"
        
        # Check generated models content for evidence of SQLAlchemy code
        models_content = models_file.read_text()
        assert "from sqlalchemy import" in models_content
        assert "declarative_base()" in models_content
        
        # We don't have LLM hooked up, so the schema is empty logically in the mock SchemaDesigner
        # but the files should have been generated.
