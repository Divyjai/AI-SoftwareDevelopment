from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime
from app.domain.models.project_graph import ProjectGraph, GraphNode, GraphEdge
from app.domain.models.database import SchemaSnapshot

class DatabaseGraph(ProjectGraph):
    """
    A specialized graph for representing the database schema and its internal relationships.
    Separated from ProjectGraph to prevent bloating the application graph.
    """
    pass

@dataclass
class DatabaseGraphVersion:
    version: str
    parent_version: str
    schema_snapshot: SchemaSnapshot
    created_at: datetime
    graph: DatabaseGraph
