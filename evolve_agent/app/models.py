from typing import Any, Dict, Optional

from pydantic import BaseModel


class WorkflowImport(BaseModel):
    yaml_content: Optional[str] = None
    yaml_url: Optional[str] = None
    app_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


class WorkflowRun(BaseModel):
    inputs: Dict[str, Any]
    files: Optional[list] = None
