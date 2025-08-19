import logging

from fastapi import UploadFile

from extracto.common.config.config_store import ConfigStore
from extracto.db.base import DBConnection
from extracto.storage.blob_client import BlobStorageClient, setup_blob_resource
from extracto.storage.istorage_client import StorageObjectType
from extracto.storage.storage_config import BlobLocation
from extracto.db.model import Document
from extracto.utils.response_model import DocumentResponse
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
        blob_config = BlobConfig()
        container_name = blob_config.BLOB_CONTAINER_NAME
        session = DBConnection().get_session()
        blob_client: BlobStorageClient = setup_blob_resource()
        try:
            blob_absolute_path = get_storage_absolute_path(projectId=projectId, documentId=documentId, documentName=documentFile.filename)

            blob_storage_path = BlobLocation(container_name=container_name, absolute_path=blob_absolute_path)

            storage_obj = blob_client.save_file(
                file_data=documentFile.file.read(),
                storage_location=blob_storage_path,
                object_type=StorageObjectType.binary.value
            )

            if storage_obj.code != 0:
                logger.error(f"Failed to save the file to blob storage")
                raise Exception(f"Failed to save the file to blob storage")

            document: Document = Document(
                ID=documentId,
                NAME=documentFile.filename,
                TYPE=documentType,
                PROJECT_ID=projectId,
                FOLDER_NAME=folderName,
                STORAGE_PATH=blob_storage_path.dict(),
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
        document_bytes = None
        session = DBConnection().get_session()
        blob_client = setup_blob_resource()
        try:
            document = session.query(Document).filter(Document.ID==documentId).first()
            storage_path = document.STORAGE_PATH
            if storage_path:
                document_bytes = blob_client.load_file(storage_location=storage_path)
        except Exception as e:
            print(f"Exception in listing documents: {e}")
            raise Exception(f"Exception in listing documents: {e}")
        finally:
            session.commit()
            session.close()
        return document_bytes

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
