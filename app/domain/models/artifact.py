from dataclasses import dataclass, field
from typing import Any, List
from enum import Enum

class ArtifactState(Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    VALIDATED = "validated"
    APPROVED = "approved"
    MERGED = "merged"
    ARCHIVED = "archived"

@dataclass
class Artifact:
    id: str
    version: str
    owner: str
    status: ArtifactState
    content: Any
    produced_by_task: str = ""
    depends_on: List[str] = field(default_factory=list)
    depended_by: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
