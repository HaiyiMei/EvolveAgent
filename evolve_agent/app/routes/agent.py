from typing import Any, Dict

from fastapi import APIRouter

from evolve_agent.agents.core import Agent
from evolve_agent.app.services.n8n_service import N8nService

router = APIRouter()
agent = Agent()
n8n_service = N8nService()


@router.post("/generate_workflow")
async def generate_workflow(prompt: str) -> Dict[str, Any]:
    """Generate a new n8n workflow based on the prompt."""
    workflow_json = agent.generate_workflow(prompt)
    return await n8n_service.create_workflow(workflow_json)
