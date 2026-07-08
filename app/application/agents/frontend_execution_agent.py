from app.domain.models.agent import BaseAgent
from app.domain.models.agent_context import AgentContext
from app.domain.models.artifact import Artifact, ArtifactState, ArtifactType
from app.domain.models.frontend_provider import NextJSProvider
from app.domain.models.frontend_plan import LogicalFrontendPlan
from app.services.frontend_generators import ComponentGenerator, RouteGenerator, ThemeGenerator, LayoutGenerator
import json

class FrontendExecutionAgent(BaseAgent):
    def run(self, context: AgentContext):
        self.prepare(context)
        self.plan()
        self.act()
        self.validate()
        self.report()

    def prepare(self, context: AgentContext):
        self.context = context
        # Find the LogicalFrontendPlan artifact
        self.logical_plan_artifact = None
        for artifact in self.context.project_state.artifacts:
            if artifact.type == ArtifactType.PLAN and "LogicalFrontendPlan" in str(artifact.metadata.get("type", "")):
                self.logical_plan_artifact = artifact
                break
                
        assert self.logical_plan_artifact is not None, "FrontendExecutionAgent requires a LogicalFrontendPlan artifact"
        
        bundle = self.context.knowledge_service.build_context(
            task=self.context.task,
            agent_name="frontend_execution",
            manager_name="frontend_manager",
            execution_id=self.context.correlation_id
        )
        self.compiled_prompt = self.context.compiler.compile(bundle)

    def plan(self):
        # We deserialize the logical plan
        plan_data = json.loads(self.logical_plan_artifact.content)
        self.logical_plan = LogicalFrontendPlan(**plan_data)
        
        # Translate Logical to Physical using Provider
        self.provider = NextJSProvider()
        self.physical_plan = self.provider.translate(self.logical_plan)

    def act(self):
        self.generated_files = []
        
        # 1. LayoutGenerator
        layout_gen = LayoutGenerator()
        self.generated_files.extend(layout_gen.generate([], self.context)) # Mock
        
        # 2. RouteGenerator
        route_gen = RouteGenerator()
        self.generated_files.extend(route_gen.generate(self.logical_plan.pages, self.context))
        
        # 3. ComponentGenerator
        comp_gen = ComponentGenerator()
        self.generated_files.extend(comp_gen.generate(self.logical_plan.component_intentions, self.context))
        
        # 4. ThemeGenerator
        theme_gen = ThemeGenerator()
        self.generated_files.extend(theme_gen.generate(self.logical_plan.design_system, self.context))
        
        # API, Form, State generators would also run here...
        
        # Generate the PhysicalFrontendPlan artifact to track this translation
        self.physical_plan.generated_artifacts = [f["path"] for f in self.generated_files]

    def validate(self):
        assert self.generated_files, "No valid files generated from Generator Pipeline"
        for file in self.generated_files:
            assert "path" in file, "File path missing"
            assert "content" in file, "File content missing"

    def report(self):
        # Save PhysicalFrontendPlan
        plan_artifact = Artifact(
            id=f"art-physical-plan-{self.context.task.id}",
            version="v1",
            owner="frontend_execution",
            status=ArtifactState.GENERATED,
            type=ArtifactType.PLAN,
            content=json.dumps(self.physical_plan.__dict__, default=lambda o: o.__dict__),
            produced_by_task=self.context.task.id,
            metadata={"type": "PhysicalFrontendPlan"}
        )
        self.context.repository.save(plan_artifact)
        self.context.project_state.artifacts.append(plan_artifact)

        artifacts = []
        for i, file in enumerate(self.generated_files):
            source_artifact = Artifact(
                id=f"art-{self.context.task.id}-src-{i}",
                version="v1",
                owner="frontend_execution",
                status=ArtifactState.GENERATED,
                type=ArtifactType.SOURCE_FILE,
                content=file["content"],
                produced_by_task=self.context.task.id,
                metadata={"path": file["path"]}
            )
            
            self.context.repository.save(source_artifact)
            self.context.project_state.artifacts.append(source_artifact)
            artifacts.append(source_artifact)
            
        # The WorkflowCoordinator passes execution to the next step.
