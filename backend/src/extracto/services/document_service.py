import logging

from fastapi import UploadFile
import uuid

from extracto.db.azure.base import DBConnection
from extracto.common.storage.s3_file_manager import S3FileManager
from extracto.common.storage.schema import S3Location
from extracto.db.model import Document, Project, User
from extracto.schema.response import DocumentResponse
from extracto.utils.util import get_storage_absolute_path
from extracto.utils.util import get_unique_number, get_current_datetime

logger = logging.getLogger(__name__)


class DocumentService:

    def __init__(self, user: User):
        self.user = user
        self.created_at = get_current_datetime()
        self.modified_at = get_current_datetime()

    async def list(self):
        """
        Fetch documents grouped by project and folder.
        - If user is Admin → fetch all projects/documents.
        - Else → fetch only projects owned by the logged-in user.
        """
        session = DBConnection().get_session()
        response = []
        try:
            print(f"Fetching documents for user {self.user.ID} with role {self.user.ROLE}...")

            # Check if user is admin
            if self.user.ROLE and self.user.ROLE.lower() == "admin":
                projects = session.query(Project).all()
            else:
                projects = session.query(Project).filter(Project.OWNER == self.user.ID).all()

            for project in projects:
                project_entry = {
                    "projectId": str(project.ID),
                    "projectName": project.NAME,
                    "folders": {}
                }

                # Fetch documents under this project
                documents = (
                    session.query(Document)
                    .filter(Document.PROJECT_ID == project.ID)
                    .all()
                )

                for doc in documents:
                    folder_name = doc.FOLDER_NAME or "root"

                    if folder_name not in project_entry["folders"]:
                        project_entry["folders"][folder_name] = []

                    project_entry["folders"][folder_name].append(self.response(document=doc))

                # Convert dict → list for folders
                project_entry["folders"] = [
                    {
                        "folderName": fname,
                        "documents": docs
                    } for fname, docs in project_entry["folders"].items()
                ]

                response.append(project_entry)

            print("Successfully fetched grouped documents.")

        except Exception as e:
            session.rollback()
            print(f"Exception in listing documents: {e}")
            raise Exception(f"Exception in listing documents: {e}")
        finally:
            session.commit()
            session.close()

        return response

    async def create(self, projectId: str,  documentFile: UploadFile, documentType: str, folderName: str):
        response = None
        documentId = get_unique_number()
        session = DBConnection().get_session()
        file_manager = S3FileManager()
        try:
            file_data = documentFile.file.read()
            project: Project = session.query(Project).filter(Project.ID==projectId).first()
            if not project:
                raise Exception(f"Project doesn't exist. Please create the project first.")

            doc_storage_path = get_storage_absolute_path(projectId=projectId, documentId=documentId, documentName=documentFile.filename)
            file_manager.create(file_data=file_data, remote_path=doc_storage_path)
            document: Document = Document(
                ID=documentId,
                NAME=documentFile.filename,
                TYPE=documentType,
                PROJECT_ID=projectId,
                FOLDER_NAME=folderName,
                STORAGE_PATH=S3Location(absolute_path=doc_storage_path).dict(),
                CREATED_AT=self.created_at,
                MODIFIED_AT=self.modified_at
            )
            session.add(document)
            response = self.response(document=document)
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in uploading the document: {e}")
            raise Exception(f"Exception in uploading the document: {e}")
        finally:
            session.commit()
            session.close()
        return response

    async def list_based_on_project(self, projectId: str):
        """
        Fetch documents grouped by project and folder.
        - If user is Admin → fetch all projects/documents.
        - Else → fetch only projects owned by the logged-in user.
        """
        session = DBConnection().get_session()
        response = {}
        try:
            print(f"Fetching documents for user {self.user.ID} with role {self.user.ROLE}...")

            # Check if user is admin
            if self.user.ROLE and self.user.ROLE.lower() == "admin":
                projects = session.query(Project).all()
            else:
                if projectId:
                    projects = (session.query(Project).filter(Project.OWNER == self.user.ID).filter
                                    (Project.ID == projectId).all())
                else:
                    projects = session.query(Project).filter(Project.OWNER == self.user.ID).all()

            for project in projects:
                project_entry = {
                    "projectId": str(project.ID),
                    "projectName": project.NAME,
                    "folders": {}
                }

                # Fetch documents under this project
                documents = (
                    session.query(Document)
                    .filter(Document.PROJECT_ID == project.ID)
                    .all()
                )

                for doc in documents:
                    folder_name = doc.FOLDER_NAME or "root"

                    if folder_name not in project_entry["folders"]:
                        project_entry["folders"][folder_name] = []

                    project_entry["folders"][folder_name].append(self.response(document=doc))

                # Convert dict → list for folders
                project_entry["folders"] = [
                    {
                        "folderName": fname,
                        "documents": docs
                    } for fname, docs in project_entry["folders"].items()
                ]

                response = project_entry

            print("Successfully fetched grouped documents.")

        except Exception as e:
            session.rollback()
            print(f"Exception in listing documents: {e}")
            raise Exception(f"Exception in listing documents: {e}")
        finally:
            session.commit()
            session.close()

        return response

    async def get(self, documentId: str):
        response = None
        session = DBConnection().get_session()
        try:
            document: Document = session.query(Document).filter(
                Document.ID == documentId).first()
            response = self.response(document=document)
        except Exception as e:
            print(f"Exception in listing documents: {e}")
            raise Exception(f"Exception in listing documents: {e}")
        finally:
            session.commit()
            session.close()
        return response

    async def delete(self, documentId: str):
        response = None
        session = DBConnection().get_session()
        try:

            document: Document = session.query(Document).filter(Document.ID==documentId).delete()
            response = self.response(document=document)
        except Exception as e:
            print(f"Exception in deleting the document: {e}")
            raise Exception(f"Exception in deleting the document: {e}")
        finally:
            session.commit()
            session.close()
        return response

    async def download(self, documentId: str):
        session = DBConnection().get_session()
        file_manager = S3FileManager()
        try:
            document = session.query(Document).filter(Document.ID == documentId).first()
            storage_path = S3Location(**document.STORAGE_PATH).absolute_path
            document_bytes = file_manager.read(remote_path=storage_path)
            return document_bytes, document.NAME
        except Exception as e:
            print(f"Exception in listing documents: {e}")
            raise Exception(f"Exception in listing documents: {e}")
        finally:
            session.commit()
            session.close()

    def response(self, document: Document):
        return DocumentResponse(
            projectId=document.PROJECT_ID,
            folderName=document.FOLDER_NAME,
            documentId=document.ID,
            documentName=document.NAME,
            storagePath=document.STORAGE_PATH,
            createdTs=document.CREATED_AT,
            modifiedTs=document.MODIFIED_AT
        )
