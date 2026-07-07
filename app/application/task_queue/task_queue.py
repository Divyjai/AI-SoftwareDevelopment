from typing import List
from app.domain.models.task import Task

class TaskQueue:
    def __init__(self):
        self.queue: List[Task] = []
        
    def enqueue(self, task: Task):
        self.queue.append(task)
        
    def dequeue(self) -> Task:
        return self.queue.pop(0) if self.queue else None
