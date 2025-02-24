import pytest

from evolve_agent.app.utils import load_workflow_template


def test_load_llm_with_webhook_template(llm_with_webhook_workflow):
    """Test loading the LLM with webhook workflow template."""
    # Verify basic structure
    assert "name" in llm_with_webhook_workflow
    assert "nodes" in llm_with_webhook_workflow
    assert "connections" in llm_with_webhook_workflow
    assert "settings" in llm_with_webhook_workflow

    # Verify nodes
    nodes = llm_with_webhook_workflow["nodes"]
    assert len(nodes) == 4  # Should have trigger, HTTP request, and Set nodes


def test_load_nonexistent_template():
    """Test attempting to load a non-existent template."""
    with pytest.raises(FileNotFoundError):
        load_workflow_template("nonexistent_template")
