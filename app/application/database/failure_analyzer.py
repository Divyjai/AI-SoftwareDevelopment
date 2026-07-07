from app.domain.models.database import DatabaseFailure

class DatabaseFailureAnalyzer:
    def analyze(self, raw_output: str) -> DatabaseFailure:
        """
        Deterministically parses Alembic/SQLAlchemy execution logs.
        """
        if "DuplicateColumn" in raw_output or "already exists" in raw_output.lower():
            return DatabaseFailure("Duplicate Column", raw_output, impacted_elements=[])
        elif "ForeignKeyViolation" in raw_output or "foreign key constraint fails" in raw_output.lower():
            return DatabaseFailure("FK Violation", raw_output, impacted_elements=[])
        elif "NotNullViolation" in raw_output or "null value in column" in raw_output.lower():
            return DatabaseFailure("Not Null Violation", raw_output, impacted_elements=[])
            
        return DatabaseFailure("Unknown Constraint Failure", raw_output, impacted_elements=[])
