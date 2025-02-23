from typing import Optional

import yaml
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..models import WorkflowImport, WorkflowRun
from ..services import make_dify_request

router = APIRouter()


@router.post("/import")
async def import_workflow(workflow: WorkflowImport):
    """Import a workflow from YAML content or URL."""
    data = {
        "mode": "yaml-content" if workflow.yaml_content else "yaml-url",
        "yaml_content": workflow.yaml_content,
        "yaml_url": workflow.yaml_url,
        "app_id": workflow.app_id,
        "name": workflow.name,
        "description": workflow.description,
    }

    return await make_dify_request("POST", "api/workflows/imports", json=data)


@router.post("/run/{workflow_id}")
async def run_workflow(workflow_id: str, workflow_run: WorkflowRun):
    """Run a specific workflow."""
    data = {"inputs": workflow_run.inputs, "files": workflow_run.files}

    return await make_dify_request("POST", f"api/workflows/{workflow_id}/run", json=data)


@router.get("/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """Get the status of a workflow run."""
    return await make_dify_request("GET", f"api/workflows/{workflow_id}/status")


@router.post("/stop/{task_id}")
async def stop_workflow(task_id: str):
    """Stop a running workflow."""
    return await make_dify_request("POST", f"api/workflows/{task_id}/stop")


@router.post("/upload")
async def upload_workflow_file(file: UploadFile = File(...), app_id: Optional[str] = Form(None)):
    """Upload a YAML file to create/update a workflow."""
    content = await file.read()
    try:
        # Validate YAML format
        yaml_content = yaml.safe_load(content)

        # Create form data
        files = {"file": (file.filename, content, "application/x-yaml")}
        data = {"app_id": app_id} if app_id else {}

        return await make_dify_request("POST", "api/workflows/upload", files=files, data=data)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"Invalid YAML format: {str(e)}")


@router.get("/apps")
async def list_apps():
    """List all available apps."""
    return await make_dify_request("GET", "api/apps")
