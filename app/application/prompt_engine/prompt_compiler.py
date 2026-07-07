from .prompt_renderer import PromptRenderer
from .models import CompiledPrompt
from app.application.knowledge.bundle import KnowledgeBundle

class PromptCompiler:
    def __init__(self, base_dir: str):
        # We don't need ContextBuilder here anymore, KnowledgeAssembler handles it
        self.renderer = PromptRenderer()
        
    def compile(self, bundle: KnowledgeBundle) -> CompiledPrompt:
        rendered = self.renderer.render(bundle)
        
        return CompiledPrompt(
            system_context=bundle.system_context,
            manager_context=bundle.agent_settings.get("manager_name", ""),
            agent_context=bundle.agent_settings.get("agent_name", ""),
            workflow_context=bundle.workflow,
            task_context=bundle.current_task.description,
            project_state=bundle.project_summary,
            memory=str(bundle.relevant_memories),
            rendered_prompt=rendered
        )
