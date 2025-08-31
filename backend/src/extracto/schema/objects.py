from pydantic import BaseModel, Field
from typing import List


class ProjectWorkflow(BaseModel):
    workflowId: str = ""
    workflowType: str = ""
    workflowName: str = ""


class ProjectRequestSchema(BaseModel):
    projectName: str = Field(default=..., description="Name of the project")
    workflow: List[ProjectWorkflow] = Field(default=list, description="Workflow associated with the project")
    tags: list = Field(default=list, description="Tags assigned to the project")
    description: str = Field(default=str, description="Project description")


class TaskRequestSchema(BaseModel):
    documentIds: List