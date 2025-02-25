from typing import Any, Dict, Set, Tuple

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from evolve_agent.agents.core import Agent
from evolve_agent.app.schemas.agent import PipelineRequest, WorkflowRequest
from evolve_agent.app.services.n8n_service import N8nService

router = APIRouter()
agent = Agent()
n8n_service = N8nService()

# Track active WebSocket connections by client address
active_clients: Set[str] = set()
connection_logger_ids: Dict[str, int] = {}


def get_client_id(websocket: WebSocket) -> str:
    """Get a unique client identifier from a WebSocket connection."""
    return f"{websocket.client.host}:{websocket.client.port}"


async def cleanup_client(client_id: str):
    """Clean up resources for a client connection."""
    active_clients.discard(client_id)
    if client_id in connection_logger_ids:
        try:
            logger.remove(connection_logger_ids.pop(client_id))
        except Exception as e:
            logger.error(f"Error removing logger for {client_id}: {e}")
    logger.info(f"Cleaned up connection for {client_id}")


@router.websocket("/logs")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for streaming logs."""
    client_id = get_client_id(websocket)

    # Handle duplicate connections
    if client_id in active_clients:
        logger.warning(f"Rejected duplicate connection from {client_id}")
        try:
            await websocket.close(code=1008, reason="Connection already exists for this client")
        except Exception as e:
            logger.error(f"Error closing duplicate connection for {client_id}: {e}")
        return

    try:
        await websocket.accept()
        active_clients.add(client_id)
        logger.info(f"New connection accepted from {client_id}")

        # Create a custom sink that sends logs to the WebSocket
        async def websocket_sink(message):
            try:
                if client_id in active_clients:  # Only send if client is still active
                    await websocket.send_text(f"{message}")
            except Exception:
                await cleanup_client(client_id)  # Clean up if we can't send

        # Add the WebSocket sink to logger
        logger_id = logger.add(websocket_sink, format="{time:HH:mm:ss} | {message}", level="INFO")
        connection_logger_ids[client_id] = logger_id

        try:
            while True:
                await websocket.receive_text()  # Keep the connection alive
        except WebSocketDisconnect:
            logger.info(f"WebSocket connection closed for {client_id}")
        except Exception as e:
            logger.error(f"WebSocket error for {client_id}: {str(e)}")
    finally:
        await cleanup_client(client_id)


@router.post("/generate_workflow")
async def generate_workflow(request: WorkflowRequest) -> Dict[str, Any]:
    """Generate a new n8n workflow based on the prompt."""
    workflow_json = agent.rag_generate_workflow(request.prompt)
    return await n8n_service.create_workflow(workflow_json)


@router.post("/pipeline")
async def pipeline(request: PipelineRequest) -> Dict[str, Any]:
    """Generate a new n8n workflow based on the prompt with iterative refinement."""
    return await agent.pipeline(request.prompt, request.max_iteration)
