from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional


class ProjectWorkflow(BaseModel):
    workflowId: str = ""
    workflowType: str = ""
    workflowName: str = ""


class ProjectRequestSchema(BaseModel):
    projectName: str = Field(default="", description="Name of the project")
    workflow: List[ProjectWorkflow] = Field(default=None, description="Workflow associated with the project")
    tags: list = Field(default=[], description="Tags assigned to the project")
    description: str = Field(default="", description="Project description")


class TaskRequestSchema(BaseModel):
    documentIds: List


class UserRequestModel(BaseModel):
    userName: str
    name: str
    emailId: str
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str]
    is_active: bool
    is_verified: bool

    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class LoginSchema(BaseModel):
    email: EmailStr
    password: str
