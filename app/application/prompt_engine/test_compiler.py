import sys
from pathlib import Path
sys.path.append(str(Path(r"c:\Users\divay\adk-project")))

from app.application.prompt_engine.prompt_compiler import PromptCompiler
from app.shared.state.project_state import ProjectState
from app.domain.models.task import Task

def test_compiler():
    compiler = PromptCompiler(r"c:\Users\divay\adk-project")
    task = Task(id="T-1", description="Build a Todo API using FastAPI", status="Created")
    state = ProjectState()
    
    compiled = compiler.compile("planner", "head_manager", task, state)
    
    assert compiled.rendered_prompt != "", "Rendered prompt is empty"
    assert "Constitutional Rule 1" in compiled.system_context, "Engineering rules not found in context"
    assert "Build a Todo API" in compiled.task_context, "Task info missing"
    
    print("VALIDATION SUCCESS: Prompt Compiler produces a valid CompiledPrompt.")

if __name__ == "__main__":
    test_compiler()
