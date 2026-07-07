from app.domain.models.task import Task
from .engine import KnowledgeEngine
from .bundle import KnowledgeBundle

class KnowledgeService:
    def __init__(self, engine: KnowledgeEngine):
        self.engine = engine
        
    def build_context(self, task: Task, agent_name: str, manager_name: str, execution_id: str) -> KnowledgeBundle:
        return self.engine.build_context(task, agent_name, manager_name, execution_id)
