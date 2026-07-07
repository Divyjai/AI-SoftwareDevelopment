from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

class MemoryType(Enum):
    PROJECT = "PROJECT"
    TASK = "TASK"
    ARTIFACT = "ARTIFACT"
    PROMPT = "PROMPT"
    EXECUTION = "EXECUTION"
    FAILURE = "FAILURE"
    KNOWLEDGE = "KNOWLEDGE"

class MemorySource(Enum):
    USER = "USER"
    PLANNER = "PLANNER"
    BACKEND_AGENT = "BACKEND_AGENT"
    HEALER = "HEALER"
    EXECUTION = "EXECUTION"
    QA = "QA"

@dataclass
class MemoryRecord:
    id: str
    memory_type: MemoryType
    workflow_id: str
    task_id: str
    agent_id: str
    summary: str
    created_at: float
    updated_at: float
    artifact_ids: List[str] = field(default_factory=list)
    execution_id: Optional[str] = None
    embedding_id: Optional[str] = None
    importance: float = 1.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Versioning
    version: int = 1
    parent_memory_id: Optional[str] = None
    supersedes_id: Optional[str] = None
    is_latest: bool = True
    
    # Source
    source: MemorySource = MemorySource.USER

    @classmethod
    def create(cls, 
               memory_type: MemoryType,
               workflow_id: str,
               task_id: str,
               agent_id: str,
               summary: str,
               artifact_ids: List[str] = None,
               execution_id: Optional[str] = None,
               embedding_id: Optional[str] = None,
               importance: float = 1.0,
               tags: List[str] = None,
               metadata: Dict[str, Any] = None,
               parent_memory_id: Optional[str] = None,
               supersedes_id: Optional[str] = None,
               version: int = 1,
               source: MemorySource = MemorySource.USER) -> "MemoryRecord":
        now = datetime.utcnow().timestamp()
        return cls(
            id=f"mem-{uuid.uuid4().hex[:8]}",
            memory_type=memory_type,
            workflow_id=workflow_id,
            task_id=task_id,
            agent_id=agent_id,
            summary=summary,
            created_at=now,
            updated_at=now,
            artifact_ids=artifact_ids or [],
            execution_id=execution_id,
            embedding_id=embedding_id,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
            version=version,
            parent_memory_id=parent_memory_id,
            supersedes_id=supersedes_id,
            is_latest=True,
            source=source
        )

@dataclass
class PromptMemory(MemoryRecord):
    def __post_init__(self):
        if self.memory_type != MemoryType.PROMPT:
            self.memory_type = MemoryType.PROMPT

@dataclass
class ExecutionMemory(MemoryRecord):
    def __post_init__(self):
        if self.memory_type != MemoryType.EXECUTION:
            self.memory_type = MemoryType.EXECUTION

@dataclass
class ArtifactMemory(MemoryRecord):
    def __post_init__(self):
        if self.memory_type != MemoryType.ARTIFACT:
            self.memory_type = MemoryType.ARTIFACT

@dataclass
class FailureMemory(MemoryRecord):
    def __post_init__(self):
        if self.memory_type != MemoryType.FAILURE:
            self.memory_type = MemoryType.FAILURE
