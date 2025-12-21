import logging

from fastapi import UploadFile
import uuid

from extracto.db.azure.base import DBConnection
from extracto.common.storage.s3_file_manager import S3FileManager
from extracto.common.storage.schema import S3Location
from extracto.db.model import WorkflowConfig, WorkflowConfig, User
from extracto.schema.response import DocumentResponse
from extracto.utils.util import get_storage_absolute_path
from extracto.utils.util import get_unique_number, get_current_datetime

logger = logging.getLogger(__name__)


class WorkflowService:

    def __init__(self, user: User):
        self.user = user
        self.created_at = get_current_datetime()
        self.timestamp = get_current_datetime()

    async def list(self):
        """
        Fetch documents grouped by workflow and folder.
        - If user is Admin → fetch all workflows/documents.
        - Else → fetch only workflows owned by the logged-in user.
        """
        session = DBConnection().get_session()
        response = []
        try:
            logger.info(f"Fetching documents for user {self.user.ID} with role {self.user.ROLE}...")

            if self.user.ROLE and self.user.ROLE.lower() == "admin":
                workflows = session.query(WorkflowConfig).all()
            else:
                workflows = session.query(WorkflowConfig).filter(WorkflowConfig.OWNER == self.user.ID).all()

            for workflow in workflows:
                workflow_entry = {
                    "workflowId": str(workflow.ID),
                    "workflowName": workflow.NAME,
                    "createdTs": workflow.CREATED_AT,
                    "modifiedTs": workflow.MODIFIED_AT 
                }

                response.append(workflow_entry)

            logger.info("Successfully fetched grouped documents.")

        except Exception as e:
            session.rollback()
            logger.error(f"Exception in listing documents: {e}")
            raise Exception(f"Exception in listing documents: {e}")
        finally:
            session.commit()
            session.close()

        return response
    
    async def create(self, workflowFile: UploadFile, workflowType: str):
        response = None
        workflowId = get_unique_number()
        session = DBConnection().get_session()
        file_manager = S3FileManager()
        try:
            file_data = workflowFile.file.read()
            doc_storage_path = get_storage_absolute_path(workflowId=workflowId, workflowId=workflowId, documentName=workflowFile.filename)
            file_manager.create(file_data=file_data, remote_path=doc_storage_path)

            workflow: WorkflowConfig = WorkflowConfig(
                ID=workflowId,
                NAME=workflowFile.filename,
                TYPE=workflowType,
                STORAGE_PATH=S3Location(absolute_path=doc_storage_path).dict(),
                CREATED_AT=self.timestamp,
                MODIFIED_AT=self.timestamp
            )
            session.add(workflow)
            response = self.response(workflow=workflow)
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in uploading the workflow: {e}")
            raise Exception(f"Exception in uploading the workflow: {e}")
        finally:
            session.commit()
            session.close()
        return response
    
    async def update(self, workflowFile: UploadFile, workflowType: str):
        response = None
        workflowId = get_unique_number()
        session = DBConnection().get_session()
        file_manager = S3FileManager()
        try:
            file_data = workflowFile.file.read()
            workflow: WorkflowConfig = session.query(WorkflowConfig).filter(WorkflowConfig.ID==workflowId).first()
            if not workflow:
                raise Exception(f"Workflow config doesn't exist. Please create the workflow first.")

            doc_storage_path = get_storage_absolute_path(workflowId=workflowId, workflowId=workflowId, documentName=workflowFile.filename)
            file_manager.create(file_data=file_data, remote_path=doc_storage_path)
            workflow: WorkflowConfig = WorkflowConfig(
                ID=workflowId,
                NAME=workflowFile.filename,
                TYPE=workflowType,
                STORAGE_PATH=S3Location(absolute_path=doc_storage_path).dict(),
                CREATED_AT=self.timestamp,
                MODIFIED_AT=self.timestamp
            )
            session.add(workflow)
            response = self.response(workflow=workflow)
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in uploading the workflow: {e}")
            raise Exception(f"Exception in uploading the workflow: {e}")
        finally:
            session.commit()
            session.close()
        return response

    async def get(self, workflowId: str):
        response = None
        session = DBConnection().get_session()
        try:
            workflow: WorkflowConfig = session.query(WorkflowConfig).filter(
                WorkflowConfig.ID == workflowId).first()
            response = self.response(workflow=workflow)
        except Exception as e:
            logger.error(f"Exception in listing documents: {e}")
            raise Exception(f"Exception in listing documents: {e}")
        finally:
            session.commit()
            session.close()
        return response

    async def delete(self, workflowId: str):
        response = None
        session = DBConnection().get_session()
        try:
            workflow: WorkflowConfig = session.query(WorkflowConfig).filter(WorkflowConfig.ID==workflowId).delete()
            response = self.response(workflow=workflow)
        except Exception as e:
            logger.error(f"Exception in deleting the workflow: {e}")
            raise Exception(f"Exception in deleting the workflow: {e}")
        finally:
            session.commit()
            session.close()
        return response

    async def download(self, workflowId: str):
        session = DBConnection().get_session()
        file_manager = S3FileManager()
        try:
            workflow = session.query(WorkflowConfig).filter(WorkflowConfig.ID == workflowId).first()
            storage_path = S3Location(**workflow.STORAGE_PATH).absolute_path
            document_bytes = file_manager.read(remote_path=storage_path)
            return document_bytes, workflow.NAME
        except Exception as e:
            logger.error(f"Exception in listing documents: {e}")
            raise Exception(f"Exception in listing documents: {e}")
        finally:
            session.commit()
            session.close()

    def response(self, workflow: WorkflowConfig):
        return DocumentResponse(
            workflowId=workflow.ID,
            workflowName=workflow.NAME,
            createdTs=workflow.CREATED_AT,
            modifiedTs=workflow.MODIFIED_AT
        )
