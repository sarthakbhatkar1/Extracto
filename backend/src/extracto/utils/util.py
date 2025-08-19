from pydantic import BaseModel
from typing import Any
from uuid import uuid4
from datetime import datetime


class JsonResponse(BaseModel):
    success: bool = False
    error: dict = {}
    result: Any = {}


def get_unique_number():
    return str(uuid4()).lower()


def get_current_datetime():
    UTC_ISO_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.000Z"
    return datetime.utcnow().strftime(UTC_ISO_TIME_FORMAT)
