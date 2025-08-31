import logging

from fastapi import UploadFile

from extracto.db.azure.base import DBConnection
from extracto.common.storage.s3_file_manager import S3FileManager
from extracto.common.storage.schema import S3Location
from extracto.db.model import Document
from extracto.schema.response import DocumentResponse
from extracto.utils.util import get_storage_absolute_path
from extracto.utils.util import get_unique_number, get_current_datetime

logger = logging.getLogger(__name__)


class DocumentService:

    def __init__(self):
        self.created_ts = get_current_datetime()
        self.modified_ts = get_current_datetime()

    async def list(self):
        response = []
        session = DBConnection().get_session()
        try:
            print(f"Fetching the documents from the database.")
            documents: [Document] = session.query(Document).all()
            print(f"Successfully fetched the documents from the database.")
            for document in documents:
                response.append(self.response(document=document))
        except Exception as e:
            print(f"Exception in listing documents: {e}")
            raise Exception(f"Exception in listing documents: {e}")
        finally:
            session.commit()
            session.close()
        print("Starting to list down the documents...")
        return response

    async def create(self, projectId: str,  documentFile: UploadFile, documentType: str, folderName: str):
        response = None
        documentId = get_unique_number()
        session = DBConnection().get_session()
        file_manager = S3FileManager()
        try:
            file_data = documentFile.file.read()
            doc_storage_path = get_storage_absolute_path(projectId=projectId, documentId=documentId, documentName=documentFile.filename)
            file_manager.create(file_data=file_data, remote_path=doc_storage_path)
            document: Document = Document(
                ID=documentId,
                NAME=documentFile.filename,
                TYPE=documentType,
                PROJECT_ID=projectId,
                FOLDER_NAME=folderName,
                STORAGE_PATH=S3Location(absolute_path=doc_storage_path).dict(),
                CREATED_TS=self.created_ts,
                MODIFIED_TS=self.modified_ts
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

    async def get(self, documentId: str):
        response = None
        session = DBConnection().get_session()
        try:
            document: Document = session.query(Document).filter(Document.ID==documentId).first()
            response = self.response(document=document)
        except Exception as e:
            print(f"Exception in listing documents: {e}")
            raise Exception(f"Exception in listing documents: {e}")
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
            createdTs=document.CREATED_TS,
            modifiedTs=document.MODIFIED_TS
        )
