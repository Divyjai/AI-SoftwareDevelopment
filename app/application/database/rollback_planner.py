from app.domain.models.database import MigrationPlan, MigrationSafety

class RollbackPlanner:
    def can_rollback(self, plan: MigrationPlan) -> bool:
        # Destructive and irreversible migrations often cannot be automatically rolled back safely
        for mig in plan.migrations:
            if mig.safety_level == MigrationSafety.IRREVERSIBLE:
                return False
        return True
        
    def generate_rollback_script(self, plan: MigrationPlan) -> str:
        if not self.can_rollback(plan):
            return "# Rollback not possible for IRREVERSIBLE changes"
        
        script = "-- Rollback Script\n"
        # Reverse the order
        for mig in reversed(plan.migrations):
            if mig.down_script:
                script += f"{mig.down_script}\n"
        return script
