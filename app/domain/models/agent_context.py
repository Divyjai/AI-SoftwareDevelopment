from dataclasses import dataclass
from typing import Any
from app.domain.models.task import Task
from app.shared.state.project_state import ProjectState
from app.interfaces.artifact_repository import ArtifactRepository
from app.interfaces.event_bus import EventBus
from app.application.prompt_engine.prompt_compiler import PromptCompiler
from app.interfaces.execution_engine import ExecutionEngine
from app.interfaces.llm_client import LLMClient

from app.application.knowledge.service import KnowledgeService

@dataclass
class AgentContext:
    task: Task
    project_state: ProjectState
    repository: ArtifactRepository
    event_bus: EventBus
    compiler: PromptCompiler
    execution_engine: ExecutionEngine
    knowledge_service: KnowledgeService
    settings: dict
    llm: LLMClient
    correlation_id: str

