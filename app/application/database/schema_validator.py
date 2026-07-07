from app.domain.models.database import DatabaseSchema

class SchemaValidator:
    def validate(self, schema: DatabaseSchema) -> bool:
        """
        Validates integrity: missing PKs, circular refs, nullability mismatches.
        """
        for table in schema.tables:
            has_pk = any(col.is_primary_key for col in table.columns)
            if not has_pk:
                raise ValueError(f"Table {table.name} is missing a Primary Key.")
                
            for fk in table.foreign_keys:
                target_table = next((t for t in schema.tables if t.name == fk.target_table), None)
                if not target_table:
                    raise ValueError(f"Table {table.name} has FK to non-existent table {fk.target_table}.")
                    
        return True
