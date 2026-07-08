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

class ArtifactType(Enum):
    PLAN = "plan"
    SOURCE_FILE = "source_file"
    PAGE = "page"
    LAYOUT = "layout"
    COMPONENT = "component"
    HOOK = "hook"
    STYLE = "style"
    API_CLIENT = "api_client"
    TEST = "test"
    ASSET = "asset"
    CONFIG = "config"
    THEME = "theme"
    FORM = "form"

@dataclass
class Artifact:
    id: str
    version: str
    owner: str
    status: ArtifactState
    type: ArtifactType = ArtifactType.SOURCE_FILE
    content: Any
    produced_by_task: str = ""
    depends_on: List[str] = field(default_factory=list)
    depended_by: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
