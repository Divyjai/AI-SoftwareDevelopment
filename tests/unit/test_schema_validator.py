import pytest
from app.application.database.schema_validator import SchemaValidator
from app.domain.models.database import DatabaseSchema, TableDefinition, ColumnDefinition, ForeignKeyDefinition

def test_missing_primary_key_raises_error():
    validator = SchemaValidator()
    schema = DatabaseSchema()
    
    table = TableDefinition(name="users")
    table.columns.append(ColumnDefinition(name="username", data_type="VARCHAR(255)"))
    schema.tables.append(table)
    
    with pytest.raises(ValueError, match="is missing a Primary Key"):
        validator.validate(schema)

def test_invalid_foreign_key_target_raises_error():
    validator = SchemaValidator()
    schema = DatabaseSchema()
    
    table = TableDefinition(name="tasks")
    table.columns.append(ColumnDefinition(name="id", data_type="INTEGER", is_primary_key=True))
    table.columns.append(ColumnDefinition(name="user_id", data_type="INTEGER"))
    table.foreign_keys.append(ForeignKeyDefinition(
        column_name="user_id", 
        target_table="users", # Note: 'users' table does not exist
        target_column="id"
    ))
    schema.tables.append(table)
    
    with pytest.raises(ValueError, match="has FK to non-existent table users"):
        validator.validate(schema)

def test_valid_schema_passes():
    validator = SchemaValidator()
    schema = DatabaseSchema()
    
    users_table = TableDefinition(name="users")
    users_table.columns.append(ColumnDefinition(name="id", data_type="INTEGER", is_primary_key=True))
    schema.tables.append(users_table)
    
    tasks_table = TableDefinition(name="tasks")
    tasks_table.columns.append(ColumnDefinition(name="id", data_type="INTEGER", is_primary_key=True))
    tasks_table.foreign_keys.append(ForeignKeyDefinition(
        column_name="user_id",
        target_table="users",
        target_column="id"
    ))
    schema.tables.append(tasks_table)
    
    assert validator.validate(schema) is True
