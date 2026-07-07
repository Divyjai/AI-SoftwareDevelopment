import os
from pathlib import Path
from app.shared.state.project_state import ProjectState

class ContextBuilder:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        
    def get_system_context(self) -> str:
        content = []
        for f in ["system_context.md", "architecture.md", "engineering_rules.md", "workflow.md"]:
            p = self.base_dir / "app/context/system" / f
            if p.exists():
                content.append(p.read_text())
        return "\n\n".join(content)

    def get_manager_context(self, manager_name: str) -> str:
        p = self.base_dir / f"app/context/managers/{manager_name}.md"
        return p.read_text() if p.exists() else ""

    def get_agent_context(self, agent_name: str) -> str:
        p = self.base_dir / f"app/context/agents/{agent_name}.md"
        return p.read_text() if p.exists() else ""

    def get_workflow_context(self) -> str:
        # Usually static or based on current phase
        p = self.base_dir / "app/context/system/workflow.md"
        return p.read_text() if p.exists() else ""

    def get_task_context(self, task) -> str:
        if not task: return ""
        return f"Task ID: {task.id}\nDescription: {task.description}\nStatus: {task.status}"

    def get_project_state(self, state: ProjectState) -> str:
        if not state: return ""
        return f"Branch: {state.branch}\nMetrics: {state.metrics}"

    def get_memory(self, memory: dict) -> str:
        return str(memory)
