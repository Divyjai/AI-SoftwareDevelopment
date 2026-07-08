from app.domain.models.agent import BaseAgent
from app.domain.models.agent_context import AgentContext
from app.domain.models.artifact import Artifact, ArtifactState, ArtifactType
from app.domain.models.frontend_plan import LogicalFrontendPlan, APIContract, DesignSystem, UIPattern
import json

class FrontendPlanner(BaseAgent):
    def run(self, context: AgentContext):
        self.prepare(context)
        self.plan()
        self.act()
        self.validate()
        self.report()

    def prepare(self, context: AgentContext):
        self.context = context
        bundle = self.context.knowledge_service.build_context(
            task=self.context.task,
            agent_name="frontend_planner",
            manager_name="frontend_manager",
            execution_id=self.context.correlation_id
        )
        self.compiled_prompt = self.context.compiler.compile(bundle)
        
    def plan(self):
        from app.domain.models.llm import PromptRequest, ModelConfig
        
        system_instruction = (
            "You are an expert Frontend Architect. "
            "You must output ONLY valid JSON representing a LogicalFrontendPlan. "
            "Select components ONLY from this official catalog: Button, Card, Table, Input, Select, Dialog, Modal, Tabs, Toast, Badge, Avatar, Skeleton, Pagination."
        )
        
        request = PromptRequest(
            compiled_prompt=self.compiled_prompt.rendered_prompt,
            system_prompt=system_instruction,
            model_config=ModelConfig(
                model="gemini-1.5-pro",
                temperature=0.2
            )
        )
        
        self.llm_response = self.context.llm.generate(request)
        
    def act(self):
        try:
            plan_data = json.loads(self.llm_response.generated_text)
            
            api_contracts = []
            for contract_data in plan_data.get("api_contracts", []):
                api_contracts.append(APIContract(
                    method=contract_data.get("method", "GET"),
                    path=contract_data.get("path", ""),
                    headers=contract_data.get("headers", {}),
                    query=contract_data.get("query", {}),
                    request=contract_data.get("request", {}),
                    response=contract_data.get("response", {}),
                    errors=contract_data.get("errors", []),
                    authentication=contract_data.get("authentication", ""),
                    rate_limits=contract_data.get("rate_limits", ""),
                    pagination=contract_data.get("pagination", "")
                ))
                
            self.frontend_plan = LogicalFrontendPlan(
                pages=plan_data.get("pages", []),
                user_flows=plan_data.get("user_flows", []),
                navigation=plan_data.get("navigation", {}),
                api_contracts=api_contracts,
                ui_patterns=plan_data.get("ui_patterns", []),
                component_intentions=plan_data.get("component_intentions", []),
                state_strategy=plan_data.get("state_strategy", ""),
                design_system=DesignSystem(**plan_data.get("design_system", {}))
            )
        except json.JSONDecodeError:
            self.frontend_plan = None
            print(f"Failed to parse JSON from LLM: {self.llm_response.generated_text}")

    def validate(self):
        assert self.frontend_plan is not None, "Failed to generate valid FrontendPlan"
        
    def report(self):
        artifact = Artifact(
            id=f"art-plan-{self.context.task.id}",
            version="v1",
            owner="frontend_planner",
            status=ArtifactState.GENERATED,
            type=ArtifactType.PLAN,
            content=json.dumps(self.frontend_plan.__dict__, default=lambda o: o.__dict__),
            produced_by_task=self.context.task.id,
            metadata={"type": "LogicalFrontendPlan"}
        )
        
        self.context.repository.save(artifact)
        self.context.project_state.artifacts.append(artifact)
        
        # In a real workflow coordinator setup, the coordinator pulls this artifact.
