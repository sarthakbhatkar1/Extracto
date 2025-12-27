import os
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel


class RoleEnum(str, Enum):
    ADMIN = "Admin"
    USER = "User"


class JsonResponse(BaseModel):
    success: bool = False
    error: dict = {}
    result: Any = {}


def get_unique_number():
    return str(uuid4()).lower()


def get_current_datetime():
    UTC_ISO_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.000Z"
    return datetime.utcnow().strftime(UTC_ISO_TIME_FORMAT)


def get_storage_absolute_path(projectId: str, documentId: str, documentName: str):
    return os.path.join("Extracto", f"{projectId}", f"{documentId}", f"{documentName}")