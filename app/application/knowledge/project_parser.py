import ast
import os
from pathlib import Path
from app.domain.models.project_graph import ProjectGraph, GraphNode, GraphEdge, NodeType, EdgeType

class PythonProjectParser:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.graph = ProjectGraph()

    def parse(self) -> ProjectGraph:
        for root, dirs, files in os.walk(self.workspace_path):
            dirs[:] = [d for d in dirs if d not in {'.venv', 'venv', '__pycache__', '.git'}]
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    self._parse_file(file_path)
        
        self._resolve_imports()
        self._resolve_calls()
        return self.graph

    def _get_module_name(self, file_path: Path) -> str:
        try:
            rel_path = file_path.relative_to(self.workspace_path)
        except ValueError:
            return file_path.stem
        
        parts = list(rel_path.parts)
        if parts[-1].endswith('.py'):
            parts[-1] = parts[-1][:-3]
        if parts[-1] == '__init__':
            parts.pop()
        return ".".join(parts)

    def _parse_file(self, file_path: Path):
        try:
            rel_path = str(file_path.relative_to(self.workspace_path))
        except ValueError:
            rel_path = str(file_path)
            
        file_id = f"file:{rel_path}"
        module_name = self._get_module_name(file_path)
        module_id = f"module:{module_name}"
        
        # 1. Create MODULE node
        module_node = GraphNode(
            id=module_id, type=NodeType.MODULE, name=module_name, file_path=rel_path
        )
        if module_id not in self.graph.nodes:
            self.graph.add_node(module_node)
            
        # 2. Create FILE node
        file_node = GraphNode(
            id=file_id, type=NodeType.FILE, name=file_path.name, file_path=rel_path,
            metadata={"module": module_name, "calls": []}
        )
        self.graph.add_node(file_node)
        
        # Link Module -> File
        self.graph.add_edge(GraphEdge(source_id=module_id, target_id=file_id, type=EdgeType.CONTAINS))

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content, filename=str(file_path))
            
            visitor = ASTVisitor(self.graph, file_node, rel_path)
            visitor.visit(tree)
            
        except Exception as e:
            pass

    def _resolve_imports(self):
        # Map module paths to file_ids
        module_to_file_id = {}
        for node in self.graph.nodes.values():
            if node.type == NodeType.FILE:
                mod = node.metadata.get("module")
                if mod:
                    module_to_file_id[mod] = node.id

        # Link IMPORTS
        for node in list(self.graph.nodes.values()):
            if node.type == NodeType.FILE:
                imports = node.metadata.get("imports", [])
                for imp in imports:
                    target_module = imp.get("module")
                    if target_module and target_module in module_to_file_id:
                        target_id = module_to_file_id[target_module]
                        self.graph.add_edge(GraphEdge(
                            source_id=node.id,
                            target_id=target_id,
                            type=EdgeType.IMPORTS
                        ))

    def _resolve_calls(self):
        # Map function names to func_ids for naive resolution
        func_name_to_id = {}
        for node in self.graph.nodes.values():
            if node.type in [NodeType.FUNCTION, NodeType.TEST]:
                # store the bare name
                func_name_to_id[node.name] = node.id
                
        # Link CALLS
        for node in list(self.graph.nodes.values()):
            if node.type == NodeType.FILE:
                calls = node.metadata.get("calls", [])
                for call in calls:
                    source_func_id = call.get("source_func_id")
                    target_func_name = call.get("target_func_name")
                    if source_func_id and target_func_name in func_name_to_id:
                        target_id = func_name_to_id[target_func_name]
                        # Don't add self edges for recursion unless needed
                        if source_func_id != target_id:
                            self.graph.add_edge(GraphEdge(
                                source_id=source_func_id,
                                target_id=target_id,
                                type=EdgeType.CALLS
                            ))

class ASTVisitor(ast.NodeVisitor):
    def __init__(self, graph: ProjectGraph, file_node: GraphNode, file_path: str):
        self.graph = graph
        self.file_node = file_node
        self.file_path = file_path
        self.current_parent = file_node
        self.imports = []
        self.calls = []
        self.current_func_id = None

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append({"module": alias.name, "name": alias.name})
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            for alias in node.names:
                self.imports.append({"module": node.module, "name": alias.name})
        self.generic_visit(node)
        
    def visit_Call(self, node):
        if self.current_func_id:
            if isinstance(node.func, ast.Name):
                self.calls.append({
                    "source_func_id": self.current_func_id,
                    "target_func_name": node.func.id
                })
            elif isinstance(node.func, ast.Attribute):
                self.calls.append({
                    "source_func_id": self.current_func_id,
                    "target_func_name": node.func.attr
                })
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        class_id = f"class:{self.file_path}:{node.name}"
        decorators = self._extract_decorators(node.decorator_list)
        class_node = GraphNode(
            id=class_id,
            type=NodeType.CLASS,
            name=node.name,
            file_path=self.file_path,
            metadata={"decorators": decorators}
        )
        self.graph.add_node(class_node)
        self.graph.add_edge(GraphEdge(
            source_id=self.current_parent.id,
            target_id=class_id,
            type=EdgeType.CONTAINS
        ))

        old_parent = self.current_parent
        self.current_parent = class_node
        self.generic_visit(node)
        self.current_parent = old_parent

    def visit_FunctionDef(self, node):
        func_id = f"func:{self.file_path}:{node.name}"
        node_type = NodeType.FUNCTION
        if node.name.startswith("test_"):
            node_type = NodeType.TEST
            
        decorators = self._extract_decorators(node.decorator_list)
        
        func_node = GraphNode(
            id=func_id,
            type=node_type,
            name=node.name,
            file_path=self.file_path,
            metadata={"decorators": decorators}
        )
        self.graph.add_node(func_node)
        self.graph.add_edge(GraphEdge(
            source_id=self.current_parent.id,
            target_id=func_id,
            type=EdgeType.CONTAINS
        ))
        
        # Check for FastAPI decorators
        for dec in decorators:
            dec_name = dec.get("name", "")
            # e.g., app.get, router.post
            if "get" in dec_name or "post" in dec_name or "put" in dec_name or "delete" in dec_name:
                method = dec_name.split(".")[-1].upper()
                args = dec.get("args", [])
                path = args[0] if args else "unknown"
                endpoint_id = f"endpoint:{method} {path}"
                endpoint_node = GraphNode(
                    id=endpoint_id,
                    type=NodeType.ENDPOINT,
                    name=f"{method} {path}",
                    file_path=self.file_path
                )
                self.graph.add_node(endpoint_node)
                self.graph.add_edge(GraphEdge(
                    source_id=endpoint_id,
                    target_id=func_id,
                    type=EdgeType.HANDLES
                ))

        old_parent = self.current_parent
        old_func = self.current_func_id
        self.current_parent = func_node
        self.current_func_id = func_id
        self.generic_visit(node)
        self.current_parent = old_parent
        self.current_func_id = old_func

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)
        
    def _extract_decorators(self, decorator_list):
        decs = []
        for dec in decorator_list:
            if isinstance(dec, ast.Name):
                decs.append({"name": dec.id})
            elif isinstance(dec, ast.Call):
                name = ""
                if isinstance(dec.func, ast.Name):
                    name = dec.func.id
                elif isinstance(dec.func, ast.Attribute):
                    name = f"{dec.func.value.id}.{dec.func.attr}" if isinstance(dec.func.value, ast.Name) else dec.func.attr
                args = [a.value for a in dec.args if isinstance(a, ast.Constant)]
                decs.append({"name": name, "args": args})
        return decs
        
    def visit_Module(self, node):
        self.generic_visit(node)
        self.file_node.metadata["imports"] = self.imports
        self.file_node.metadata["calls"] = self.calls
