from app.domain.models.project_graph import ProjectGraph, CoverageStatus, EdgeType
import re

class CoverageAnalyzer:
    def analyze(self, project_graph: ProjectGraph):
        # Scan the graph and update coverage status for nodes
        # In a real app, this parses coverage.xml or coverage.json from pytest-cov
        # Here we do a structural analysis of the graph
        
        for node_id, node in project_graph.nodes.items():
            if node.type.name in ["FUNCTION", "ENDPOINT"]:
                # Check if there's any incoming TEST edge
                incoming_edges = project_graph._adj_in.get(node_id, [])
                test_edges = [e for e in incoming_edges if e.type == EdgeType.TESTS]
                
                if not test_edges:
                    node.coverage_status = CoverageStatus.UNCOVERED
                elif len(test_edges) >= 1:
                    node.coverage_status = CoverageStatus.COVERED
                    
        # Calculate specific coverage metrics based on node types
        functions = [n for n in project_graph.nodes.values() if n.type.name == "FUNCTION"]
        endpoints = [n for n in project_graph.nodes.values() if n.type.name == "ENDPOINT"]
        modules = [n for n in project_graph.nodes.values() if n.type.name == "MODULE"]
        
        covered_functions = [n for n in functions if n.coverage_status == CoverageStatus.COVERED]
        covered_endpoints = [n for n in endpoints if n.coverage_status == CoverageStatus.COVERED]
        covered_modules = [n for n in modules if n.coverage_status == CoverageStatus.COVERED]
        
        project_graph.coverage_metrics.function_coverage = len(covered_functions) / len(functions) if functions else 0.0
        project_graph.coverage_metrics.endpoint_coverage = len(covered_endpoints) / len(endpoints) if endpoints else 0.0
        project_graph.coverage_metrics.module_coverage = len(covered_modules) / len(modules) if modules else 0.0
        
        # In a real app we'd get line and branch coverage from pytest-cov XML
        project_graph.coverage_metrics.line_coverage = 0.85 # Mocked for demo
        project_graph.coverage_metrics.branch_coverage = 0.80 # Mocked for demo
        
        coverable_nodes = functions + endpoints
        covered_nodes = covered_functions + covered_endpoints
        
        if coverable_nodes:
            return len(covered_nodes) / len(coverable_nodes)
        return 0.0
