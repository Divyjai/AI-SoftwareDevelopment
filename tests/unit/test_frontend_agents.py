import pytest
from app.domain.models.frontend_plan import LogicalFrontendPlan, APIContract, DesignSystem, UIPattern
from app.application.workflows.frontend_workflow import create_frontend_workflow

def test_logical_frontend_plan_structure():
    contract = APIContract(
        method="GET",
        path="/api/v1/projects",
        headers={"Authorization": "Bearer token"},
        query={"status": "active"},
        request={},
        response={"data": []},
        authentication="JWT",
        errors=[{"code": "401", "message": "Unauthorized"}],
        rate_limits="100/min",
        pagination="cursor"
    )
    
    design_system = DesignSystem(
        colors={"primary": "#000000"}
    )
    
    plan = LogicalFrontendPlan(
        pages=[{"path": "/dashboard", "layout_type": "Admin"}],
        api_contracts=[contract],
        design_system=design_system
    )
    
    assert len(plan.pages) == 1
    assert plan.api_contracts[0].path == "/api/v1/projects"
    assert plan.design_system.colors["primary"] == "#000000"

def test_frontend_workflow_creation():
    workflow = create_frontend_workflow()
    
    assert workflow.execution_id.startswith("frontend-workflow-")
    assert "frontend_planner" in workflow.steps
    assert "frontend_execution" in workflow.steps
    assert "api_integration" in workflow.steps
    
    # Check dependencies
    assert "frontend_planner" in workflow.steps["frontend_execution"].dependencies
    assert "frontend_execution" in workflow.steps["api_integration"].dependencies
