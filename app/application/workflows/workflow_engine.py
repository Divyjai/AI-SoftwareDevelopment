from app.application.task_queue.task_queue import TaskQueue
from app.domain.models.task import Task, TaskState

class WorkflowEngine:
    def __init__(self, task_queue: TaskQueue):
        self.task_queue = task_queue
        
    def process_task_breakdown(self, breakdown_artifact):
        tasks_data = breakdown_artifact.content.get("tasks", [])
        for t_data in tasks_data:
            task = Task(id=t_data["id"], description=t_data["description"], status=TaskState.CREATED)
            self.task_queue.enqueue(task)
