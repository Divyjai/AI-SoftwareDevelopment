from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

# --- Enums ---

class MigrationSafety(Enum):
    SAFE = auto()          # e.g., create table, add index
    WARNING = auto()       # e.g., add nullable column, rename column
    DESTRUCTIVE = auto()   # e.g., drop table
    IRREVERSIBLE = auto()  # e.g., drop column, delete data

class SeedProfile(Enum):
    MINIMAL = auto()
    DEVELOPMENT = auto()
    TESTING = auto()
    DEMO = auto()
    PERFORMANCE = auto()

class DataType(Enum):
    STRING = auto()
    INTEGER = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    DATETIME = auto()
    JSON = auto()
    UUID = auto()
    RELATION = auto()

# --- Logical Schema ---

@dataclass
class AttributeDefinition:
    name: str
    type: DataType
    is_primary: bool = False
    is_required: bool = True
    is_unique: bool = False
    default_value: Any = None
    description: str = ""

@dataclass
class RelationshipDefinition:
    name: str
    target_entity: str
    relation_type: str # "one-to-many", "many-to-many", "one-to-one"
    is_cascade: bool = False
    join_table: Optional[str] = None

@dataclass
class EntityDefinition:
    name: str
    attributes: List[AttributeDefinition] = field(default_factory=list)
    relationships: List[RelationshipDefinition] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

# --- Physical Schema ---

@dataclass
class ColumnDefinition:
    name: str
    data_type: str  # e.g. "VARCHAR(255)", "INTEGER"
    is_primary_key: bool = False
    is_nullable: bool = False
    is_unique: bool = False
    default_expression: Optional[str] = None

@dataclass
class ForeignKeyDefinition:
    column_name: str
    target_table: str
    target_column: str
    on_delete: str = "NO ACTION"
    on_update: str = "NO ACTION"

@dataclass
class ConstraintDefinition:
    name: str
    constraint_type: str # "CHECK", "UNIQUE", etc.
    expression: str

@dataclass
class IndexDefinition:
    name: str
    columns: List[str]
    is_unique: bool = False

@dataclass
class ViewDefinition:
    name: str
    sql_definition: str

@dataclass
class TriggerDefinition:
    name: str
    sql_definition: str

@dataclass
class StoredProcedureDefinition:
    name: str
    sql_definition: str

@dataclass
class TableDefinition:
    name: str
    columns: List[ColumnDefinition] = field(default_factory=list)
    foreign_keys: List[ForeignKeyDefinition] = field(default_factory=list)
    constraints: List[ConstraintDefinition] = field(default_factory=list)
    indexes: List[IndexDefinition] = field(default_factory=list)

@dataclass
class DatabaseSchema:
    tables: List[TableDefinition] = field(default_factory=list)
    views: List[ViewDefinition] = field(default_factory=list)
    triggers: List[TriggerDefinition] = field(default_factory=list)
    stored_procedures: List[StoredProcedureDefinition] = field(default_factory=list)

# --- Versioning & Observability ---

@dataclass
class SchemaSnapshot:
    snapshot_id: str
    schema_version: str
    created_at: datetime
    checksum: str
    database_schema: DatabaseSchema
    execution_id: str

@dataclass
class MigrationScript:
    migration_id: str
    up_script: str
    down_script: Optional[str] = None
    safety_level: MigrationSafety = MigrationSafety.WARNING

@dataclass
class MigrationPlan:
    plan_id: str
    migrations: List[MigrationScript] = field(default_factory=list)
    is_safe: bool = True

@dataclass
class MigrationHistory:
    migration_id: str
    version: str
    checksum: str
    execution_id: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: str = "PENDING"
    rollback_available: bool = False

@dataclass
class DatabaseHealth:
    is_connected: bool
    latency_ms: float
    active_connections: int

@dataclass
class DatabaseMetrics:
    migration_duration_ms: float = 0.0
    rows_affected: int = 0

@dataclass
class DatabaseMemory:
    schema_summary: str = ""
    migration_summary: str = ""
    constraint_fix: str = ""
    repair_strategy: str = ""
    database_type: str = ""
    orm_type: str = ""

@dataclass
class DatabaseFailure:
    failure_type: str
    raw_output: str
    impacted_elements: List[str] = field(default_factory=list)

@dataclass
class DatabaseRepairPlan:
    repair_id: str
    failure: DatabaseFailure
    proposed_solution: str
    sql_patch: Optional[str] = None

@dataclass
class DatabaseConnection:
    uri: str
    dialect: str

@dataclass
class DatabaseConfig:
    connection: DatabaseConnection
    pool_size: int = 5
    ssl_enabled: bool = False

@dataclass
class SeedPlan:
    profile: SeedProfile
    target_tables: List[str] = field(default_factory=list)
    script_content: str = ""
