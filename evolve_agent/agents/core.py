import datetime
import json
from pathlib import Path
from textwrap import dedent
from typing import Any, Dict

from langchain.schema import AIMessage, HumanMessage, SystemMessage
from loguru import logger

from ..app.services.n8n_service import N8nService
from ..app.utils import log_context
from .models import get_model
from .prompt import escape_template, get_reflection_prompt, get_system_prompt
from .rag import TemplateRAG

project_root = Path(__file__).parent.parent
cache_dir = project_root / "logs" / "cache"


class WorkflowExecutionError(Exception):
    """Custom exception for workflow execution errors."""

    def __init__(
        self,
        message: str,
        stage: str,
        workflow: Dict[str, Any] = None,
        original_error: Exception = None,
    ):
        self.message = message
        self.stage = stage
        self.workflow = workflow
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self):
        return f"{self.stage}: {self.message}\nWorkflow: {self.workflow}"


def get_error_msg(stage: str, message: str) -> str:
    return dedent(
        f"""\
        There are some errors in the previous workflow.
        The workflow generation process is as follows:
        1. generate_workflow
        2. create_workflow
        3. get_webhook_input
        4. activate_workflow
        5. call_webhook

        And the error is in the step: {stage}
        With the following error message:
        {message}
        """
    )


class Agent:
    def __init__(self, max_retries: int = 5):
        self.agent_meta, _ = get_model(model_id="openai/gpt-4o", format="json", temperature=0.8)
        rag_model, rag_embeddings = get_model(model_id="openai/gpt-4o-mini", format="json", temperature=0.2)
        self.agent_rag = TemplateRAG(model=rag_model, embeddings=rag_embeddings)
        self.agent_input, _ = get_model(model_id="openai/gpt-4o-mini", format="json", temperature=0.2)

        self.n8n_service = N8nService()
        self.max_retries = max_retries

    def rag_generate_workflow(
        self,
        prompt: str,
        archive: str = None,
        errors: str = None,
        guidelines: str = None,
    ) -> Dict[str, Any]:
        logger.info("[Agent] RAG agent generating workflow")
        response = self.agent_rag.query(prompt, archive, errors, guidelines)
        workflow = json.loads(response["answer"])
        logger.info(f"[Agent] Generated workflow: {workflow['name']}")
        return workflow

    def get_webhook_input(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[Agent] Getting webhook input for workflow: {workflow['name']}")
        prompt = f"""
        You are an expert at understanding and explaining workflow templates.
        And you are given the following template information:
        {escape_template(workflow)}

        There is a webhook in the template. Provide the input for the webhook. Make sure to return in a WELL-FORMED JSON object.
        """
        response = self.agent_input.invoke(prompt).content
        webhook_input = json.loads(response)
        # XXX: hardcoded for webhook input
        if "body" in webhook_input:
            webhook_input = webhook_input["body"]
        logger.info(f"[Agent] Got webhook input: {webhook_input}")
        return webhook_input

    async def step(
        self,
        save_dir: Path,
        step_name: str,
        prompt: str,
        archive: str = None,
        errors: str = None,
        guidelines: str = None,
    ) -> Dict[str, Any]:
        """This is the main step method that orchestrates the entire workflow generation
        and execution process.

        Steps:
            1. generate_workflow
            2. create_workflow
            3. get_webhook_input
            4. activate_workflow
            5. call_webhook
        """

        # 1. generate_workflow
        workflow = self.rag_generate_workflow(prompt, archive, errors, guidelines)
        workflow["name"] = f"{step_name}-{workflow['name']}"
        save_path = save_dir / f"{workflow['name']}.json"
        save_path.write_text(json.dumps(workflow, indent=2))
        logger.info(f"[Agent] Saved workflow to {save_path}")

        # 2. create_workflow
        try:
            created_workflow = await self.n8n_service.create_workflow(workflow, is_webhook=True)
            logger.info(f"[Agent] Created workflow: {created_workflow['name']}")
        except Exception as e:
            logger.error(f"[Agent] Error creating workflow: {e}")
            raise WorkflowExecutionError(
                message=f"Error creating workflow: {e}",
                stage="create_workflow",
                workflow=workflow,
                original_error=e,
            )

        # 3. get_webhook_input
        try:
            webhook = self.n8n_service.get_webhooks(created_workflow)[0]  # XXX: Only one webhook is supported for now
            logger.info(f"[Agent] Got webhook: {webhook}")
        except IndexError:
            raise WorkflowExecutionError(
                message="No webhook found in the workflow",
                stage="get_webhook_input",
                workflow=workflow,
            )
        except Exception as e:
            raise WorkflowExecutionError(
                message=f"Error getting webhook input: {e}",
                stage="get_webhook_input",
                workflow=workflow,
                original_error=e,
            )
        webhook_input = self.get_webhook_input(created_workflow)

        # 4. activate_workflow
        try:
            result = await self.n8n_service.activate_workflow(created_workflow["id"])
            logger.info(f"[Agent] Activated workflow: {created_workflow['id']}")
        except Exception as e:
            raise WorkflowExecutionError(
                message=f"Error activating workflow: {e}",
                stage="activate_workflow",
                workflow=workflow,
                original_error=e,
            )

        # 5. call_webhook
        try:
            logger.info(
                f"[Agent] Calling webhook: {created_workflow['id']}, {webhook.path}, {webhook.httpMethod}, {webhook_input}"
            )
            response = await self.n8n_service.call_webhook(
                webhook_path=webhook.path,
                webhook_method=webhook.httpMethod,
                data=webhook_input,
            )
            logger.info(f"[Agent] Webhook response: {response}")
        except Exception as e:
            await self.n8n_service.deactivate_workflow(created_workflow["id"])
            logger.error(f"[Agent] Error calling webhook: {e}")
            logger.info(f"[Agent] Deactivated workflow: {created_workflow['name']}")
            raise WorkflowExecutionError(
                message=f"Error calling webhook: {e}",
                stage="call_webhook",
                workflow=workflow,
                original_error=e,
            )
        return response

    async def pipeline(self, prompt: str) -> Dict[str, Any]:
        """This is the main pipeline method that orchestrates the entire workflow
        generation and execution process.

        It takes a prompt as input, generates a workflow based on the prompt, creates
        and activates the workflow, prepares the webhook input, and finally calls the
        webhook to execute the workflow.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        save_dir = cache_dir / timestamp
        save_dir.mkdir(parents=True, exist_ok=True)

        with log_context(save_dir / "log.log"):
            msg_list = [
                SystemMessage(content=get_system_prompt()),
                HumanMessage(content=prompt),
            ]
            error_msg = None
            archives = []
            for idx in range(self.max_retries):
                try:
                    logger.info(f"[Agent] Iteration {idx + 1} of {self.max_retries}")
                    logger.info("[Agent] Meta agent invoking...")
                    logger.debug(f"[Agent] Meta agent prompt:\n{msg_list}")
                    response_meta = self.agent_meta.invoke(msg_list).content
                    msg_list.append(AIMessage(content=response_meta))

                    logger.info("[Agent] RAG agent invoking...")
                    response_rag = await self.step(
                        save_dir=save_dir,
                        step_name=f"{timestamp}-{idx + 1:02d}",
                        prompt=prompt,
                        archive="\n".join(archives),
                        errors=error_msg,
                        guidelines=json.loads(response_meta)["guidelines"],
                    )
                    return response_rag
                except WorkflowExecutionError as e:
                    logger.error(f"[Agent] Error in step: {e}")
                    logger.error("[Agent] Retrying with new prompt...")
                    archive = json.dumps(e.workflow, indent=2)
                    archives.append(archive)
                    error_msg = get_error_msg(e.stage, e.message)
                    msg_list.append(HumanMessage(content=get_reflection_prompt(archive, error_msg)))

            raise Exception("Failed to generate workflow")


if __name__ == "__main__":
    import asyncio

    async def main():
        agent = Agent()
        response = await agent.pipeline(
            "How can I set up a WhatsApp chatbot that can send me weather of Singapore each hour?"
        )
        print(response)

    asyncio.run(main())
