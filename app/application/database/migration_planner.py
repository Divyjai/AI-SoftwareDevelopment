from app.domain.models.database import MigrationPlan
from app.application.database.providers import MigrationProvider

class MigrationPlanner:
    def __init__(self, provider: MigrationProvider):
        self.provider = provider
        
    def plan_migration(self, plan: MigrationPlan) -> str:
        return self.provider.generate_migration_script(plan)
