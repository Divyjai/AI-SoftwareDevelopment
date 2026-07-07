from app.domain.models.database import DatabaseSchema, MigrationPlan, MigrationScript, MigrationSafety
import uuid

class SchemaDiffer:
    """
    Compares a Current Schema (from SchemaInspector) to a Desired Schema (from SchemaDesigner)
    to calculate delta operations.
    """
    
    def compute_diff(self, current_schema: DatabaseSchema, desired_schema: DatabaseSchema) -> MigrationPlan:
        """
        Identifies tables to create, alter, drop.
        For Phase 8 demo, we assume the initial schema generation creates tables.
        """
        plan = MigrationPlan(plan_id=str(uuid.uuid4()))
        
        # Extremely simplified diff logic
        current_tables = {t.name: t for t in current_schema.tables}
        desired_tables = {t.name: t for t in desired_schema.tables}
        
        for name, table in desired_tables.items():
            if name not in current_tables:
                # Need to CREATE
                up_script = f"CREATE TABLE {name} (...);"
                down_script = f"DROP TABLE {name};"
                plan.migrations.append(MigrationScript(
                    migration_id=f"create_{name}",
                    up_script=up_script,
                    down_script=down_script,
                    safety_level=MigrationSafety.SAFE
                ))
            else:
                # Check for ALTERs (columns added/removed)
                pass
                
        for name in current_tables:
            if name not in desired_tables:
                # Need to DROP
                up_script = f"DROP TABLE {name};"
                down_script = f"CREATE TABLE {name} (...);"
                plan.migrations.append(MigrationScript(
                    migration_id=f"drop_{name}",
                    up_script=up_script,
                    down_script=down_script,
                    safety_level=MigrationSafety.DESTRUCTIVE
                ))
                plan.is_safe = False
                
        return plan
