from app.domain.models.repair import FailureReport, RepairPlan
from app.domain.models.project_graph import ProjectGraph
from typing import Optional

class RepairPlanner:
    def __init__(self, knowledge_service):
        self.knowledge_service = knowledge_service

    def plan(self, report: FailureReport, project_graph: Optional[ProjectGraph] = None) -> RepairPlan:
        files_to_modify = []
        functions_to_modify = []
        
        # 1. Start with the affected files from the report
        for file in report.affected_files:
            files_to_modify.append(file)

        # 2. Use the ProjectGraph to expand scope
        if project_graph:
            for file_path in report.affected_files:
                # Find the file node
                file_node_id = f"file:{file_path}"
                if file_node_id in project_graph.nodes:
                    # Find all functions/endpoints in this file that might be relevant
                    dependencies = project_graph.get_dependencies(file_node_id)
                    # For demo purposes, we might just pass the file context
                    pass

            # If we extracted nodes (e.g., from the LLM or parser), we would add their blast radius
            for node_id in report.affected_nodes:
                affected = project_graph.get_blast_radius(node_id)
                for node in affected:
                    if node.type.name == "FILE" and node.file_path not in files_to_modify:
                        files_to_modify.append(node.file_path)
                    elif node.type.name == "FUNCTION":
                        functions_to_modify.append(node.name)

        return RepairPlan(
            files_to_modify=list(set(files_to_modify)),
            functions_to_modify=list(set(functions_to_modify)),
            dependencies=[],
            repair_reason=f"Fixing {report.failure_type} triggered by {report.root_cause}",
            previous_similar_repairs=[],  # Would query MemoryService here
            execution_constraints=["Do not modify unchanged logic", "Ensure tests pass"]
        )
