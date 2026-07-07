from app.application.task_queue.task_queue import TaskQueue
from app.application.task_queue.task_assignment import TaskAssignmentPolicy

class TaskDispatcher:
    def __init__(self, queue: TaskQueue, policy: TaskAssignmentPolicy, agent_registry: dict):
        self.queue = queue
        self.policy = policy
        self.agents = agent_registry # mapping of agent name to agent instance
        
    def dispatch_next(self, context_factory):
        task = self.queue.dequeue()
        if not task: return None
        
        agent_name = self.policy.assign(task)
        agent = self.agents.get(agent_name)
        if agent:
            # Build context specifically for this task
            ctx = context_factory(task)
            agent.run(ctx)
            return True
        return False
