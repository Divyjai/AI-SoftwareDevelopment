from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class APIContract:
    method: str
    path: str
    headers: Dict[str, str]
    query: Dict[str, Any]
    request: Dict[str, Any]
    response: Dict[str, Any]
    errors: List[Dict[str, Any]]
    authentication: str
    rate_limits: str
    pagination: str

@dataclass
class DesignSystem:
    colors: Dict[str, str] = field(default_factory=dict)
    spacing: Dict[str, str] = field(default_factory=dict)
    typography: Dict[str, str] = field(default_factory=dict)
    radius: Dict[str, str] = field(default_factory=dict)
    shadows: Dict[str, str] = field(default_factory=dict)
    icons: str = "lucide-react"
    animations: Dict[str, str] = field(default_factory=dict)
    breakpoints: Dict[str, str] = field(default_factory=dict)
    themes: List[str] = field(default_factory=lambda: ["light", "dark", "system"])

@dataclass
class UIPattern:
    name: str
    description: str
    required_components: List[str]
    layout: str
    state: str
    api_dependencies: List[str]
    knowledge_tags: List[str]

@dataclass
class LogicalFrontendPlan:
    pages: List[Dict[str, Any]] = field(default_factory=list)
    user_flows: List[str] = field(default_factory=list)
    navigation: Dict[str, Any] = field(default_factory=dict)
    api_contracts: List[APIContract] = field(default_factory=list)
    ui_patterns: List[UIPattern] = field(default_factory=list)
    component_intentions: List[Dict[str, Any]] = field(default_factory=list)
    state_strategy: str = ""
    design_system: DesignSystem = field(default_factory=DesignSystem)

@dataclass
class PhysicalFrontendPlan:
    nextjs_routes: List[str] = field(default_factory=list)
    react_components: List[str] = field(default_factory=list)
    tailwind_classes: Dict[str, str] = field(default_factory=dict)
    folder_structure: Dict[str, Any] = field(default_factory=dict)
    providers: List[str] = field(default_factory=list)
    imports: Dict[str, List[str]] = field(default_factory=dict)
    hooks: List[str] = field(default_factory=list)
    generated_artifacts: List[str] = field(default_factory=list)
