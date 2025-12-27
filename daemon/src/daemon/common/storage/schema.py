from pydantic import BaseModel
from typing import Literal


class GenericLocation(BaseModel):
    storage_type: Literal["blob", "s3"]
    container_name: str
    absolute_path: str


class BlobLocation(GenericLocation):
    storage_type: str = "blob"


class S3Location(GenericLocation):
    storage_type: str = "s3"
    container_name: str = ""
