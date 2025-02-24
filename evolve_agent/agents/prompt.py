import json
from pathlib import Path
from typing import Any, Dict

from langchain import hub
from langchain.prompts import PromptTemplate

root = Path(__file__).parent
project_root = root.parent
templates_dir = project_root / "templates"
llm_with_webhook_template = templates_dir / "LLM_With_Webhook.json"
credentials_template = templates_dir / "credentials.json"


def escape_template(template: Dict[str, Any]) -> str:
    template_str = json.dumps(template, indent=2)
    # Escape curly braces in the JSON by replacing { with {{ and } with }}
    # escaped_template = template_str.replace("{", "{{").replace("}", "}}")
    return template_str


def get_webhook_template() -> str:
    webhook_template = json.loads(llm_with_webhook_template.read_text())
    return escape_template(webhook_template)


def get_system_prompt() -> str:
    return """You are an expert at understanding and explaining n8n workflow templates.
You need to communicate with other agents to generate a workflow.
Do give GUIDELINES to the the RAG agent which will be used to search for the best template.

Please return in JSON format like:
{
    "thought": "...",
    "guidelines": "..."
}"""


def get_reflection_prompt(archive: str, errors: str) -> str:
    return f"""Here is the previous agent RAG response:
{archive}

Errors happened in the previous workflow:
{errors}

Carefully review the proposed new architecture and reflect on the following points:

1. **Interestingness**: Assess whether your proposed architecture is interesting or innovative compared to existing methods in the archive. If you determine that the proposed architecture is not interesting, suggest a new architecture that addresses these shortcomings.
- Make sure to check the difference between the proposed architecture and previous attempts.
- Compare the proposal and the architectures in the archive CAREFULLY, including their actual differences in the implementation.
- Decide whether the current architecture is innovative.
- USE CRITICAL THINKING!

2. **Implementation Mistakes**: Identify any mistakes you may have made in the implementation. Review the code carefully, debug any issues you find, and provide a corrected version. REMEMBER checking "## WRONG Implementation examples" in the prompt.

3. **Improvement**: Based on the proposed architecture, suggest improvements in the detailed implementation that could increase its performance or effectiveness. In this step, focus on refining and optimizing the existing implementation without altering the overall design framework, except if you want to propose a different architecture if the current is not interesting.
- Observe carefully about whether the implementation is actually doing what it is supposed to do.
- Check if there is redundant code or unnecessary steps in the implementation. Replace them with effective implementation.
- Try to avoid the implementation being too similar to the previous agent.

And then, you need to improve or revise the implementation, or implement the new proposed architecture based on the reflection.

Your response should be organized as follows:
"reflection": Provide your thoughts on the interestingness of the architecture, identify any mistakes in the implementation, and suggest improvements.
"thought": Revise your previous proposal or propose a new architecture if necessary, using the same format as the example response.
"name": Provide a name for the revised or new architecture. (Don't put words like "new" or "improved" in the name.)
"guidelines": Provide the GUIDELINES to the the RAG agent which will be used to search for the best template.

Please return in JSON format like:
{{"reflection": "...",
    "thought": "...",
    "name": "...",
    "guidelines": "..."
}}"""


def get_rag_prompt() -> PromptTemplate:
    # prompt = hub.pull("rlm/rag-prompt")
    template = """You are an expert at understanding and explaining n8n workflow templates.

# Context
And you are given the following template information:
{context}

# Archive
Here is the archive of the discovered architectures:
{archive}

# Errors
Errors happened in the last archive workflow:
{errors}

# Guidelines:
{guidelines}

# Question
Answer the question based on the templates provided:

Question: {input}

# NOTED
Here is an example of the output format for the next workflow architecture:
{example}

# Credentials
Here is the credentials for some nodes in the workflow:
{credentials}

Remember to:
1. Imitate the style of the template
2. Make sure to return in a WELL-FORMED JSON object
3. Focus on the "nodes" and "connections" keys
4. DO generate the workflow using the same webhook mechanism as the example workflow provided"""

    return PromptTemplate.from_template(
        template=template,
        partial_variables={
            "example": get_webhook_template(),
            "credentials": credentials_template.read_text(),
        },
    )
