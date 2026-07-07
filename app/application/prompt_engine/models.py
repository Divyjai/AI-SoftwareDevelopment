from dataclasses import dataclass

@dataclass
class CompiledPrompt:
    system_context: str
    manager_context: str
    agent_context: str
    workflow_context: str
    task_context: str
    project_state: str
    memory: str
    rendered_prompt: str
