import pytest

from evolve_agent.app.services.n8n_service import N8nService


@pytest.mark.asyncio
async def test_create_and_execute_llm_with_webhook_workflow(n8n_service: N8nService, llm_with_webhook_workflow):
    """Test creating and executing an LLM with webhook workflow."""
    # Create the workflow
    workflow = await n8n_service.create_workflow(llm_with_webhook_workflow, is_webhook=True)
    assert workflow["id"] is not None

    # Activate the workflow
    active = await n8n_service.activate_workflow(workflow["id"])
    assert active is True

    # Call the webhook
    webhook_id = workflow["webhookIDs"][0]
    response = await n8n_service.call_webhook(webhook_id, {"content": "Hello, world!"})
    assert response["text"] is not None

    # Cleanup
    await n8n_service.delete_workflow(workflow["id"])
