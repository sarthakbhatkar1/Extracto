from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, Response, Depends

from extracto.db.model import User
from extracto.logger.log_utils import Logger
from extracto.services.document_service import DocumentService
from extracto.utils.user_dependancy import get_current_user
from extracto.utils.util import JsonResponse

logger = Logger()

document_api = APIRouter(tags=["Document Processing APIs"])


@document_api.get("")
async def list_of_documents(projectId: str = None, user: User = Depends(get_current_user)):
    json_response = JsonResponse()
    try:
        logger.info("Starting to list down the documents...")
        response = await DocumentService(user=user).list_based_on_project(projectId=projectId)
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "101", "message": f"Error in listing of documents: {e}"}
        logger.error(f'Exception in listing of documents: {e}')
    return json_response.dict()


@document_api.post("")
async def upload_document(
        projectId: str = Form(...),
        folderName: str = Form(...),
        documentType: str = Form(...),
        document: UploadFile = File(...),
        documentName: Optional[str] = Form(None),
        user: User = Depends(get_current_user)
):
    json_response = JsonResponse()
    try:
        if not documentName:
            documentName = document.filename
        response = await DocumentService(user=user).create(
            projectId=projectId, folderName=folderName,
            documentType=documentType, documentFile=document
        )
        logger.info(f"Successfully uploaded document.")
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "102", "message": f"Error in uploading of document: {e}"}
        logger.error(f'Exception in uploading document: {e}')
    return json_response.dict()


@document_api.get("/{documentId}")
async def get_document(documentId: str, user: User = Depends(get_current_user)):
    json_response = JsonResponse()
    try:
        response = await DocumentService(user=user).get(documentId=documentId)
        logger.info(f"Successfully retrieved the document with documentId: {documentId}.")
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "103", "message": f"Error in fetching the details of the document: {e}"}
        logger.error(f'Exception in fetching the document: {e}')
    return json_response.dict()


@document_api.get("/{documentId}/download")
async def download_document(documentId: str, user: User = Depends(get_current_user)):
    json_response = JsonResponse()
    try:
        response, filename = await DocumentService(user=user).download(documentId=documentId)
        logger.info(f"Successfully retrieved the document with documentId: {documentId}.")
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "103", "message": f"Error in fetching the details of the document: {e}"}
        raise Exception(f'Exception in fetching the document: {e}')
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    return Response(
        content=json_response.result,
        media_type="application/octet_stream",
        headers=headers
    )
