from app.domain.models.database import DatabaseSchema
from app.application.database.providers import ORMProvider

class ORMGenerator:
    def __init__(self, provider: ORMProvider):
        self.provider = provider
        
    def generate(self, schema: DatabaseSchema) -> str:
        return self.provider.generate_models(schema)
