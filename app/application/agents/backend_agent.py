from app.domain.models.agent import BaseAgent
from app.domain.models.agent_context import AgentContext
from app.domain.models.artifact import Artifact, ArtifactState
from app.domain.events.events import CodeGenerated

class BackendAgent(BaseAgent):
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
            agent_name="backend",
            manager_name="backend_manager",
            execution_id=self.context.correlation_id
        )
        self.compiled_prompt = self.context.compiler.compile(bundle)
        
    def plan(self):
        # We integrate the prompt construction into the plan/act phase.
        from app.domain.models.llm import PromptRequest, ModelConfig
        import json
        
        system_instruction = (
            "You are an expert backend engineer. "
            "You must output ONLY valid JSON matching this schema: "
            '{"files": [{"path": "string", "content": "string"}]}'
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
        
        # Telemetry hook - would typically be handled by the ExecutionEngine or Compiler but we attach it here
        # or we could save it to PromptRecord
        
    def act(self):
        import json
        try:
            self.parsed_response = json.loads(self.llm_response.generated_text)
            self.generated_files = self.parsed_response.get("files", [])
        except json.JSONDecodeError:
            self.generated_files = []
            print(f"Failed to parse JSON from LLM: {self.llm_response.generated_text}")

        
    def validate(self):
        assert self.generated_files, "No valid files generated from LLM"
        for file in self.generated_files:
            assert "path" in file, "File path missing"
            assert "content" in file, "File content missing"
        
    def report(self):
        artifacts = []
        for i, file in enumerate(self.generated_files):
            # Using artifact_type 'SOURCE_FILE' as requested in acceptance tests discussion
            source_artifact = Artifact(
                id=f"art-{self.context.task.id}-src-{i}",
                version="v1",
                owner="backend",
                status=ArtifactState.GENERATED,
                content=file["content"],
                produced_by_task=self.context.task.id,
                metadata={"path": file["path"]}
            )
            # monkey patch artifact_type if it doesn't exist explicitly in Artifact model
            setattr(source_artifact, 'artifact_type', 'SOURCE_FILE')
            
            self.context.repository.save(source_artifact)
            self.context.project_state.artifacts.append(source_artifact)
            artifacts.append(source_artifact)
            
        self.context.event_bus.publish(CodeGenerated(event_id=f"evt-{self.context.task.id}", timestamp=123.0))
        
        # Depending on execution engine signature, we may pass one or all artifacts.
        # For Demo 2 we execute the first or main.
        if artifacts:
            self.context.execution_engine.execute(artifacts[0], self.context)
