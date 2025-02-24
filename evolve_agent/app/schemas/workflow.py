from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class WebhookNodeParameters(BaseModel):
    httpMethod: HTTPMethod = Field(default=HTTPMethod.POST, description="HTTP method for the webhook")
    path: str = Field(description="Webhook endpoint path")
    responseMode: str = Field(default="responseNode", description="Response mode for the webhook")
    options: Dict[str, Any] = Field(default_factory=dict, description="Additional webhook options")


class WebhookNode(BaseModel):
    parameters: WebhookNodeParameters
    type: str = Field(default="n8n-nodes-base.webhook", description="Node type identifier")
    typeVersion: int = Field(default=2, description="Version of the node type")
    position: List[int] = Field(description="Position coordinates [x, y] in the workflow")
    id: str = Field(description="Unique identifier for the node")
    name: str = Field(default="Webhook", description="Display name of the node")
    webhookId: Optional[str] = Field(None, description="ID of the webhook if created")


class NodeConnection(BaseModel):
    node: str = Field(description="Target node name")
    type: str = Field(description="Connection type (e.g., 'main', 'ai_languageModel')")
    index: int = Field(default=0, description="Connection index")


class WorkflowConnections(BaseModel):
    main: List[List[NodeConnection]] = Field(default_factory=lambda: [[]], description="Main connections between nodes")


class WorkflowSettings(BaseModel):
    executionOrder: str = Field(default="v1", description="Workflow execution order version")
    saveExecutionProgress: bool = Field(default=True, description="Whether to save execution progress")
    saveManualExecutions: bool = Field(default=True, description="Whether to save manual executions")
    saveDataErrorExecution: str = Field(default="all", description="Error execution data saving policy")
    saveDataSuccessExecution: str = Field(default="all", description="Success execution data saving policy")


class WebhookWorkflow(BaseModel):
    name: str = Field(description="Name of the workflow")
    nodes: List[Any] = Field(description="List of workflow nodes")
    connections: Dict[str, Dict[str, List[List[NodeConnection]]]] = Field(description="Node connections")
    active: bool = Field(default=True, description="Whether the workflow is active")
    settings: WorkflowSettings = Field(default_factory=WorkflowSettings, description="Workflow settings")
    id: Optional[str] = Field(None, description="Workflow ID if saved")
