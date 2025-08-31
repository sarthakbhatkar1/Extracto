from datetime import datetime
from pydantic import BaseModel
from typing import Any


class DocumentResponse(BaseModel):
    projectId: str
    folderName: str
    documentId: str
    documentName: str
    storagePath: dict
    createdBy: str
    modifiedBy: str
    createdTs: datetime
    modifiedTs: datetime


class ProjectResponse(BaseModel):
    projectId: str
    projectName: str
    tags: list
    description: str
    createdBy: str
    modifiedBy: str
    createdTs: datetime
    modifiedTs: datetime


class TaskResponse(BaseModel):
    taskId: str
    output: Any
    createdTs: datetime
    modifiedTs: datetime

