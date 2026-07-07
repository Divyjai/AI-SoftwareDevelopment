from app.domain.models.task import Task, TaskState

class TaskFactory:
    def create(self, task_id: str, description: str) -> Task:
        return Task(id=task_id, description=description, status=TaskState.CREATED)
