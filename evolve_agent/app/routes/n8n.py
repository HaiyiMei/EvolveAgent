from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

from ..services.n8n_service import HTTPMethod, N8nService

router = APIRouter()
n8n_service = N8nService()


# @router.post("/workflows")
# async def create_workflow(workflow_data: Dict[str, Any]) -> Dict[str, Any]:
#     """Create a new n8n workflow."""
#     try:
#         return await n8n_service.create_workflow(workflow_data)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/import")
async def import_workflow(workflow_json: Dict[str, Any]) -> Dict[str, Any]:
    """Import a workflow from JSON data."""
    try:
        return await n8n_service.create_workflow(workflow_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import workflow: {str(e)}")


@router.get("/executions/{execution_id}")
async def get_execution_results(
    execution_id: str, include_data: bool = Query(True, description="Include detailed execution data")
) -> Dict[str, Any]:
    """Get detailed results of a workflow execution."""
    try:
        return await n8n_service.get_execution_results(execution_id, include_data)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")


@router.get("/workflows/{workflow_id}/executions")
async def get_workflow_executions(
    workflow_id: str,
    status: Optional[str] = Query(None, description="Filter by status: 'error' or 'success'"),
    limit: int = Query(100, description="Maximum number of executions to return"),
    include_data: bool = Query(True, description="Include detailed execution data"),
) -> List[Dict[str, Any]]:
    """Get all executions for a specific workflow."""
    try:
        return await n8n_service.get_workflow_executions(
            workflow_id, status=status, limit=limit, include_data=include_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhooks/{webhook_path}")
async def call_webhook(
    webhook_path: str,
    data: Dict[str, Any],
    method: str = Query("POST", description="HTTP method to use for the webhook call"),
) -> Dict[str, Any]:
    """Call a webhook with the specified path and data."""
    try:
        webhook_method = HTTPMethod(method.upper())
        return await n8n_service.call_webhook(webhook_path, webhook_method, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid HTTP method: {method}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to call webhook: {str(e)}")


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str) -> Dict[str, Any]:
    """Get workflow details by ID."""
    try:
        return await n8n_service.get_workflow(workflow_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")


@router.put("/workflows/{workflow_id}")
async def update_workflow(workflow_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing workflow."""
    try:
        return await n8n_service.update_workflow(workflow_id, workflow_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str) -> Dict[str, Any]:
    """Delete a workflow."""
    try:
        await n8n_service.delete_workflow(workflow_id)
        return {"message": f"Workflow {workflow_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/workflows")
async def delete_all_workflows(
    active: Optional[bool] = Query(None, description="Filter by active status"),
    tags: Optional[str] = Query(None, description="Filter by comma-separated tag names"),
    name: Optional[str] = Query(None, description="Filter by workflow name"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
) -> Dict[str, Any]:
    """Delete all workflows matching the given filters."""
    try:
        deleted_ids = await n8n_service.delete_all_workflows(
            active=active,
            tags=tags,
            name=name,
            project_id=project_id,
        )
        return {
            "message": f"Successfully deleted {len(deleted_ids)} workflows",
            "deleted_workflow_ids": deleted_ids,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/activate")
async def activate_workflow(workflow_id: str) -> Dict[str, Any]:
    """Activate a workflow."""
    try:
        return await n8n_service.activate_workflow(workflow_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/deactivate")
async def deactivate_workflow(workflow_id: str) -> Dict[str, Any]:
    """Deactivate a workflow."""
    try:
        return await n8n_service.deactivate_workflow(workflow_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
