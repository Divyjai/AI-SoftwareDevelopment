from app.domain.models.task import Task

class TaskAssignmentPolicy:
    def assign(self, task: Task) -> str:
        # Returns the name of the agent role to handle the task
        desc = task.description.lower()
        if "db" in desc or "database" in desc: return "DatabaseAgent"
        if "frontend" in desc or " ui " in desc: return "FrontendAgent"
        if "test" in desc: return "TestingAgent"
        if "deploy" in desc: return "DeploymentAgent"
        return "BackendAgent" # default fallback
