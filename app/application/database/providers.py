from abc import ABC, abstractmethod
from app.domain.models.database import DatabaseSchema, MigrationPlan

class ORMProvider(ABC):
    @abstractmethod
    def generate_models(self, schema: DatabaseSchema) -> str:
        pass

class MigrationProvider(ABC):
    @abstractmethod
    def generate_migration_script(self, plan: MigrationPlan) -> str:
        pass

class SQLAlchemyProvider(ORMProvider):
    def generate_models(self, schema: DatabaseSchema) -> str:
        # Dummy scaffold
        code = "from sqlalchemy import Column, Integer, String, ForeignKey\n"
        code += "from sqlalchemy.orm import declarative_base, relationship\n\n"
        code += "Base = declarative_base()\n\n"
        
        for table in schema.tables:
            # Capitalize to match typical ClassName
            class_name = table.name.capitalize()
            if class_name.endswith('s'):
                class_name = class_name[:-1]
                
            code += f"class {class_name}(Base):\n"
            code += f"    __tablename__ = '{table.name}'\n\n"
            for col in table.columns:
                sa_type = "Integer" if "INT" in col.data_type.upper() else "String"
                pk_str = ", primary_key=True" if col.is_primary_key else ""
                code += f"    {col.name} = Column({sa_type}{pk_str})\n"
            code += "\n"
            
        return code

class AlembicProvider(MigrationProvider):
    def generate_migration_script(self, plan: MigrationPlan) -> str:
        # Scaffold
        script = "def upgrade():\n"
        for mig in plan.migrations:
            script += f"    # {mig.up_script}\n    pass\n"
        script += "\ndef downgrade():\n"
        for mig in plan.migrations:
            if mig.down_script:
                script += f"    # {mig.down_script}\n    pass\n"
        return script
