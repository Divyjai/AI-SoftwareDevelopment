from app.interfaces.agent_executor import AgentExecutor

class ADKExecutor(AgentExecutor):
    async def execute(self, task):
        raise NotImplementedError()
