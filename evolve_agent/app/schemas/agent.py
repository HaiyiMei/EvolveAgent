from pydantic import BaseModel


class WorkflowRequest(BaseModel):
    prompt: str


class PipelineRequest(BaseModel):
    prompt: str
    max_iteration: int = 5
