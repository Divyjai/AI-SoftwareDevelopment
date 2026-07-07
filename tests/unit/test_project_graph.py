import os
import tempfile
from pathlib import Path
from app.domain.models.project_graph import ProjectGraph, GraphNode, GraphEdge, NodeType, EdgeType
from app.application.knowledge.project_parser import PythonProjectParser

def test_project_graph_manual():
    graph = ProjectGraph()
    
    file_a = GraphNode(id="file:a.py", type=NodeType.FILE, name="a.py", file_path="a.py")
    file_b = GraphNode(id="file:b.py", type=NodeType.FILE, name="b.py", file_path="b.py")
    
    class_a = GraphNode(id="class:a.py:ClassA", type=NodeType.CLASS, name="ClassA", file_path="a.py")
    
    graph.add_node(file_a)
    graph.add_node(file_b)
    graph.add_node(class_a)
    
    graph.add_edge(GraphEdge(source_id=file_a.id, target_id=class_a.id, type=EdgeType.CONTAINS))
    graph.add_edge(GraphEdge(source_id=file_b.id, target_id=file_a.id, type=EdgeType.IMPORTS))
    
    # Dependencies of b.py should include a.py
    deps = graph.get_dependencies(file_b.id)
    assert len(deps) == 1
    assert deps[0].id == "file:a.py"
    
    # Blast radius of a.py should include b.py (since b imports a)
    affected = graph.get_blast_radius(file_a.id)
    assert len(affected) == 1
    assert affected[0].id == "file:b.py"

def test_project_parser():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a tiny python project
        app_dir = Path(temp_dir) / "app"
        app_dir.mkdir()
        
        with open(app_dir / "models.py", "w") as f:
            f.write("""
class User:
    def get_name(self):
        return "Test"
            """)
            
        with open(app_dir / "api.py", "w") as f:
            f.write("""
from app.models import User

def get_user():
    return User()
            """)
            
        parser = PythonProjectParser(workspace_path=temp_dir)
        graph = parser.parse()
        
        # Verify nodes
        file_models = graph.get_node(f"file:app{os.sep}models.py")
        file_api = graph.get_node(f"file:app{os.sep}api.py")
        
        assert file_models is not None
        assert file_api is not None
        
        module_app_models = graph.get_node("module:app.models")
        assert module_app_models is not None
        
        class_user = graph.get_node(f"class:app{os.sep}models.py:User")
        func_get_name = graph.get_node(f"func:app{os.sep}models.py:get_name")
        func_get_user = graph.get_node(f"func:app{os.sep}api.py:get_user")
        
        assert class_user is not None
        assert func_get_name is not None
        assert func_get_user is not None
        
        # Verify relationships
        # api.py should depend on models.py
        api_deps = graph.get_dependencies(file_api.id)
        assert any(n.id == file_models.id for n in api_deps), "api.py should depend on models.py"
        
        # models.py blast radius should include api.py
        models_radius = graph.get_blast_radius(file_models.id)
        assert any(n.id == file_api.id for n in models_radius), "models.py change should affect api.py"
        
        # Test endpoints
        # Our mock api.py didn't have endpoints. Let's create one.
        with open(app_dir / "api.py", "w") as f:
            f.write("""
from app.models import User

@app.get('/users')
def get_user():
    return User().get_name()
            """)
        
        # Reparse
        parser = PythonProjectParser(workspace_path=temp_dir)
        graph = parser.parse()
        
        func_get_user = graph.get_node(f"func:app{os.sep}api.py:get_user")
        endpoint_node = graph.get_node("endpoint:GET /users")
        assert endpoint_node is not None, "Endpoint node should be created"
        
        # Verify call edge
        func_get_name = graph.get_node(f"func:app{os.sep}models.py:get_name")
        calls = graph.get_dependencies(func_get_user.id)
        assert any(n.id == func_get_name.id for n in calls), "get_user should call get_name"
