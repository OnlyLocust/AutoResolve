from pydantic import BaseModel
from typing import Optional

class Repository(BaseModel):
    full_name: str

class WorkflowRun(BaseModel):
    id: int
    name: str
    head_sha: str
    conclusion: Optional[str]
    logs_url: str

class WebhookPayload(BaseModel):
    action: str
    repository: Repository
    workflow_run: Optional[WorkflowRun] = None