from app.domain.models.database import SeedPlan, SeedProfile, DatabaseSchema

class SeedGenerator:
    def generate(self, schema: DatabaseSchema, profile: SeedProfile) -> SeedPlan:
        # Scaffold
        plan = SeedPlan(profile=profile, target_tables=[t.name for t in schema.tables])
        
        if profile == SeedProfile.MINIMAL:
            plan.script_content = "# Minimal seed data"
        elif profile == SeedProfile.DEVELOPMENT:
            plan.script_content = "# Development fixtures (rich dataset)"
        elif profile == SeedProfile.TESTING:
            plan.script_content = "# Testing fixtures (deterministic)"
        else:
            plan.script_content = "# Default seed"
            
        return plan
