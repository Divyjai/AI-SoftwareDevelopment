from app.domain.models.agent import BaseAgent
from app.application.database.schema_designer import SchemaDesigner
from app.application.database.schema_differ import SchemaDiffer
from app.application.database.schema_inspector import SchemaInspector
from app.application.database.schema_validator import SchemaValidator
from app.application.database.migration_planner import MigrationPlanner
from app.application.database.rollback_planner import RollbackPlanner
from app.application.database.migration_validator import MigrationValidator
from app.application.database.orm_generator import ORMGenerator
from app.application.database.migration_runner import MigrationRunner
from app.application.database.seed_generator import SeedGenerator
from app.application.database.providers import AlembicProvider, SQLAlchemyProvider
from app.domain.models.database import DatabaseConfig, DatabaseConnection, SeedProfile
from app.domain.models.artifact import Artifact, ArtifactState
import json

class DatabasePlanner(BaseAgent):
    def __init__(self):
        self.schema_designer = SchemaDesigner()
        self.schema_validator = SchemaValidator()
        self.schema_differ = SchemaDiffer()
        self.migration_planner = MigrationPlanner(AlembicProvider())
        self.rollback_planner = RollbackPlanner()
        self.context = None

    def prepare(self, task): pass
    def plan(self): pass
    def act(self): pass
    def validate(self): pass
    def report(self): pass

    def run(self, context, db_config: DatabaseConfig):
        self.context = context
        
        # 1. Analyze Requirements -> Logical Schema
        reqs = self.context.task.description if self.context and self.context.task else "Build a Todo Platform"
        logical_schema = self.schema_designer.design_logical_schema(reqs)
        
        # 2. Design Physical Schema
        desired_schema = self.schema_designer.design_physical_schema(logical_schema, dialect=db_config.connection.dialect)
        
        # 3. Validate Schema Integrity
        self.schema_validator.validate(desired_schema)
        
        # 4. Inspect current schema (Mock empty for Demo 5)
        # Normally: inspector = SchemaInspector(db_config); current = inspector.inspect()
        current_schema = self.schema_designer.design_physical_schema([]) # empty
        
        # 5. Schema Differ
        migration_plan = self.schema_differ.compute_diff(current_schema, desired_schema)
        
        # 6. Build Rollback Script
        rollback_script = self.rollback_planner.generate_rollback_script(migration_plan)
        
        # 7. Generate Migration Script
        migration_script = self.migration_planner.plan_migration(migration_plan)
        
        return {
            "desired_schema": desired_schema,
            "migration_plan": migration_plan,
            "migration_script": migration_script,
            "rollback_script": rollback_script
        }


class DatabaseExecutionAgent(BaseAgent):
    def __init__(self, execution_engine):
        self.orm_generator = ORMGenerator(SQLAlchemyProvider())
        self.migration_validator = MigrationValidator()
        self.migration_runner = MigrationRunner(execution_engine)
        self.seed_generator = SeedGenerator()

    def prepare(self, task): pass
    def plan(self): pass
    def act(self): pass
    def validate(self): pass
    def report(self): pass

    def run(self, plan_output: dict, db_config: DatabaseConfig):
        # 1. Generate ORM Models
        desired_schema = plan_output["desired_schema"]
        orm_code = self.orm_generator.generate(desired_schema)
        
        # 2. Validate Migration
        migration_plan = plan_output["migration_plan"]
        self.migration_validator.validate(migration_plan)
        
        # 3. Apply Migration
        # Write script to disk conceptually, then run
        success = self.migration_runner.apply("mock/path/to/script.py")
        if not success:
            raise Exception("Migration Failed")
            
        # 4. Generate Seed Data
        seed_plan = self.seed_generator.generate(desired_schema, profile=SeedProfile.DEVELOPMENT)
        
        # Return artifacts
        return [
            Artifact(
                id="art-db-models",
                version="v1",
                owner="database",
                status=ArtifactState.GENERATED,
                content=orm_code,
                metadata={"path": "app/models.py"}
            ),
            Artifact(
                id="art-db-migration",
                version="v1",
                owner="database",
                status=ArtifactState.GENERATED,
                content=plan_output["migration_script"],
                metadata={"path": f"alembic/versions/{migration_plan.plan_id}.py"}
            ),
            Artifact(
                id="art-db-seed",
                version="v1",
                owner="database",
                status=ArtifactState.GENERATED,
                content=seed_plan.script_content,
                metadata={"path": "scripts/seed.py"}
            )
        ]
