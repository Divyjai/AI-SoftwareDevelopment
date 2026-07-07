from app.application.knowledge.bundle import KnowledgeBundle

class PromptRenderer:
    def render(self, bundle: KnowledgeBundle) -> str:
        # Format lists
        mem_str = "\n".join([f"- {m.summary}" for m in bundle.relevant_memories]) if bundle.relevant_memories else "None"
        art_str = "\n".join([f"- {a.id}: {a.content[:100]}..." for a in bundle.artifacts]) if bundle.artifacts else "None"
        fail_str = "\n".join([f"- {m.summary}" for m in bundle.similar_failures]) if bundle.similar_failures else "None"
        exec_str = "\n".join([f"- ID: {e.get('execution_id')} Status: {e.get('status')}" for e in bundle.execution_history]) if bundle.execution_history else "None"
        
        graph_str = "None"
        if bundle.relevant_nodes:
            graph_str = "\n".join([f"- {n.type.name}: {n.id} ({n.name})" for n in bundle.relevant_nodes])
        
        sections = [
            "--- GOAL ---", bundle.goal,
            "--- CURRENT TASK ---", f"ID: {bundle.current_task.id}\nDescription: {bundle.current_task.description}",
            "--- SYSTEM CONTEXT ---", bundle.system_context,
            "--- WORKFLOW CONTEXT ---", bundle.workflow,
            "--- PROJECT STATE ---", bundle.project_summary,
            "--- RELEVANT GRAPH NODES ---", graph_str,
            "--- RELEVANT MEMORIES ---", mem_str,
            "--- SIMILAR FAILURES ---", fail_str,
            "--- ARTIFACTS ---", art_str,
            "--- EXECUTION HISTORY ---", exec_str
        ]
        return "\n\n".join(filter(None, sections))
