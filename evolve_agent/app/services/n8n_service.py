from typing import Any, Dict, List, Optional

import httpx

from ..config import settings


class N8nService:
    def __init__(self):
        self.base_url = settings.N8N_BASE_URL
        self.prefix = "api/v1"
        self.webhook_prefix = "webhook"
        self.api_url = f"{self.base_url}/{self.prefix}"
        self.webhook_url = f"{self.base_url}/{self.webhook_prefix}"

        self.api_key = settings.N8N_API_KEY
        self.headers = {"X-N8N-API-KEY": self.api_key, "Content-Type": "application/json"}

    @staticmethod
    def get_webhook_ids(json_data: Dict[str, Any]) -> List[str]:
        """Get the webhook IDs for a workflow."""
        webhook_ids = []
        for node in json_data["nodes"]:
            if node["type"] == "n8n-nodes-base.webhook":
                webhook_ids.append(node["parameters"]["path"])
        return webhook_ids

    @staticmethod
    def convert_json_to_workflow(json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert JSON data to a workflow.

        This is a wrapper around create_workflow that handles workflow JSON imports.
        """
        # Ensure the JSON data has the minimum required structure
        workflow_data = {
            "name": json_data.get("name", "Imported Workflow"),
            "nodes": json_data.get("nodes", []),
            "connections": json_data.get("connections", {}),
            "settings": json_data.get(
                "settings",
                {
                    "saveExecutionProgress": True,
                    "saveManualExecutions": True,
                    "saveDataErrorExecution": "all",
                    "saveDataSuccessExecution": "all",
                },
            ),
        }
        return workflow_data

    async def call_webhook(self, webhook_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call a webhook."""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.webhook_url}/{webhook_id}", headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()

    async def get_filtered_workflows(
        self,
        *,
        active: Optional[bool] = None,
        tags: Optional[str] = None,
        name: Optional[str] = None,
        project_id: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get workflows with filtering options.

        Args:
            active: Filter by active status
            tags: Filter by comma-separated tag names (e.g. "test,production")
            name: Filter by workflow name
            project_id: Filter by project ID
            limit: Maximum number of items to return (max: 250)
            cursor: Pagination cursor from previous response

        Returns:
            Dict containing workflow data and next cursor
        """
        params = {}
        if active is not None:
            params["active"] = str(active).lower()
        if tags:
            params["tags"] = tags
        if name:
            params["name"] = name
        if project_id:
            params["projectId"] = project_id
        if limit:
            params["limit"] = min(limit, 250)  # Enforce max limit of 250
        if cursor:
            params["cursor"] = cursor

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_url}/workflows", headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

    async def create_workflow(self, json_data: Dict[str, Any], is_webhook: bool = True) -> Dict[str, Any]:
        """Create a new workflow in n8n."""
        workflow_data = self.convert_json_to_workflow(json_data)
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.api_url}/workflows", headers=self.headers, json=workflow_data)
            response.raise_for_status()
            workflow = response.json()

            if is_webhook:
                workflow["webhookIDs"] = self.get_webhook_ids(json_data)
            return workflow

    async def get_execution_results(self, execution_id: str, include_data: bool = True) -> Dict[str, Any]:
        """Get the results of a workflow execution, including all outputs, warnings, and
        errors."""
        async with httpx.AsyncClient() as client:
            url = f"{self.api_url}/executions/{execution_id}"
            if include_data:
                url += "?includeData=true"
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def get_workflow_executions(
        self, workflow_id: str, status: Optional[str] = None, limit: int = 100, include_data: bool = True
    ) -> List[Dict[str, Any]]:
        """Get all executions for a specific workflow with optional filtering.

        status can be 'error', 'success', or None for all
        """
        params = {"workflowId": workflow_id, "includeData": str(include_data).lower(), "limit": limit}
        if status:
            params["status"] = status

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_url}/executions", headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()["data"]

    async def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow details by ID."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_url}/workflows/{workflow_id}", headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def update_workflow(self, workflow_id: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing workflow."""
        workflow_data = self.convert_json_to_workflow(json_data)
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.api_url}/workflows/{workflow_id}", headers=self.headers, json=workflow_data
            )
            response.raise_for_status()
            return response.json()

    async def delete_workflow(self, workflow_id: str) -> None:
        """Delete a workflow."""
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{self.api_url}/workflows/{workflow_id}", headers=self.headers)
            response.raise_for_status()

    async def delete_all_workflows(
        self,
        *,
        active: Optional[bool] = None,
        tags: Optional[str] = None,
        name: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> List[str]:
        """Delete all workflows matching the given filters.

        Args:
            active: Filter by active status before deletion
            tags: Filter by comma-separated tag names before deletion
            name: Filter by workflow name before deletion
            project_id: Filter by project ID before deletion

        Returns:
            List of deleted workflow IDs
        """
        # Get workflows matching filters
        workflows = await self.get_filtered_workflows(
            active=active,
            tags=tags,
            name=name,
            project_id=project_id,
            limit=250,  # Get maximum allowed
        )

        deleted_ids = []
        for workflow in workflows["data"]:
            await self.delete_workflow(workflow["id"])
            deleted_ids.append(workflow["id"])

        # Handle pagination to delete all matching workflows
        while workflows.get("nextCursor"):
            workflows = await self.get_filtered_workflows(
                active=active,
                tags=tags,
                name=name,
                project_id=project_id,
                limit=250,
                cursor=workflows["nextCursor"],
            )
            for workflow in workflows["data"]:
                await self.delete_workflow(workflow["id"])
                deleted_ids.append(workflow["id"])

        return deleted_ids

    async def activate_workflow(self, workflow_id: str) -> bool:
        """Activate a workflow."""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.api_url}/workflows/{workflow_id}/activate", headers=self.headers)
            response.raise_for_status()
            return response.json()["active"]

    async def deactivate_workflow(self, workflow_id: str) -> bool:
        """Deactivate a workflow."""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.api_url}/workflows/{workflow_id}/deactivate", headers=self.headers)
            response.raise_for_status()
            return response.json()["active"]
