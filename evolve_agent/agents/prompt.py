import json
from pathlib import Path

from langchain import hub

root = Path(__file__).parent
project_root = root.parent
templates_dir = project_root / "templates"
llm_with_webhook_template = templates_dir / "LLM_With_Webhook.json"


def get_webhook_template() -> str:
    webhook_template = json.loads(llm_with_webhook_template.read_text())
    webhook_template_str = json.dumps(webhook_template, indent=2)
    # Escape curly braces in the JSON by replacing { with {{ and } with }}
    escaped_template = webhook_template_str.replace("{", "{{").replace("}", "}}")
    return escaped_template


def get_rag_prompt() -> str:
    escaped_template = get_webhook_template()

    # prompt = hub.pull("rlm/rag-prompt")
    rag_prompt = f"""
    You are an expert at understanding and explaining workflow templates.
    And you are given the following template information:
    {{context}}

    Answer the question based on the templates provided:

    Question: {{input}}

    Remember to:
    1. Imitate the style of the template
    2. Make sure to return in a WELL-FORMED JSON object
    3. Focus on the "nodes" and "connections" keys
    4. DO generate the workflow using the same webhook mechanism as the following template:

    {escaped_template}
    """

    return rag_prompt
