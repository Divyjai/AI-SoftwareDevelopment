from typing import List, Dict, Any
from app.domain.models.database import (
    EntityDefinition, AttributeDefinition, RelationshipDefinition,
    DatabaseSchema, TableDefinition, ColumnDefinition, ForeignKeyDefinition,
    DataType
)

class SchemaDesigner:
    """
    Translates abstract application requirements into a Logical Schema (Entities)
    and maps that Logical Schema into a Physical Schema (Tables/Columns/Constraints).
    """
    
    def design_logical_schema(self, requirements: str) -> List[EntityDefinition]:
        # In a real implementation, the LLM processes requirements and outputs Entities.
        # Here we scaffold the logical representation.
        # E.g. "Build a Multi-tenant Todo Platform" -> Users, Orgs, Tasks...
        return []
        
    def design_physical_schema(self, logical_schema: List[EntityDefinition], dialect: str = "sqlite") -> DatabaseSchema:
        """
        Maps logical entities to physical tables.
        For example, a Many-to-Many logical relationship creates a join table.
        """
        schema = DatabaseSchema()
        
        # 1. Create tables and primary keys
        for entity in logical_schema:
            table = TableDefinition(name=f"{entity.name.lower()}s")
            # Always ensure an ID column
            table.columns.append(ColumnDefinition(
                name="id", 
                data_type="INTEGER" if dialect == "sqlite" else "SERIAL",
                is_primary_key=True,
                is_nullable=False
            ))
            
            for attr in entity.attributes:
                # Map logical types to physical
                phys_type = "VARCHAR(255)" if attr.type == DataType.STRING else "INTEGER"
                table.columns.append(ColumnDefinition(
                    name=attr.name,
                    data_type=phys_type,
                    is_nullable=not attr.is_required,
                    is_unique=attr.is_unique,
                    default_expression=str(attr.default_value) if attr.default_value else None
                ))
            schema.tables.append(table)
            
        # 2. Add foreign keys based on relationships
        # (This is a simplified mapper)
        for entity in logical_schema:
            table = next((t for t in schema.tables if t.name == f"{entity.name.lower()}s"), None)
            if not table: continue
            
            for rel in entity.relationships:
                if rel.relation_type == "one-to-many":
                    # The "many" side needs the FK
                    target_table_name = f"{rel.target_entity.lower()}s"
                    target_table = next((t for t in schema.tables if t.name == target_table_name), None)
                    if target_table:
                        fk_col_name = f"{entity.name.lower()}_id"
                        target_table.columns.append(ColumnDefinition(
                            name=fk_col_name,
                            data_type="INTEGER",
                            is_nullable=False
                        ))
                        target_table.foreign_keys.append(ForeignKeyDefinition(
                            column_name=fk_col_name,
                            target_table=table.name,
                            target_column="id",
                            on_delete="CASCADE" if rel.is_cascade else "NO ACTION"
                        ))
                        
        return schema
