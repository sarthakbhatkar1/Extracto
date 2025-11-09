from datetime import datetime
from pydantic import BaseModel
from typing import Any
from uuid import UUID


class DocumentResponse(BaseModel):
    projectId: UUID
    folderName: str
    documentId: UUID
    documentName: str
    storagePath: dict
    createdTs: datetime
    modifiedTs: datetime


class ProjectResponse(BaseModel):
    projectId: UUID
    projectName: str
    tags: list
    description: str
    owner: UUID
    createdTs: datetime
    modifiedTs: datetime


class TaskResponse(BaseModel):
    taskId: UUID
    status: str
    output: Any
    createdTs: datetime
    modifiedTs: datetime


class UserResponse(BaseModel):
    userId: UUID
    fullName: str
    email: str
    role: str
    isActive: bool
    isVerified: bool
    createdTs: datetime
    modifiedTs: datetime
