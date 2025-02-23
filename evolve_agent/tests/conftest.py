import json
from pathlib import Path
from typing import Any, Dict

import pytest

from evolve_agent.app.services.n8n_service import N8nService


@pytest.fixture
def n8n_service() -> N8nService:
    """Create a N8nService instance for testing."""
    return N8nService()


@pytest.fixture
def llm_with_webhook_workflow() -> Dict[str, Any]:
    """Load the AI agent workflow template."""
    template_path = Path("evolve_agent/templates/LLM_With_Webhook.json")
    with open(template_path, "r") as f:
        return json.load(f)
