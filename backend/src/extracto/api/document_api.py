from fastapi import APIRouter, UploadFile, File, Form, Response

from extracto.logger.log_utils import Logger
from extracto.services.document_service import DocumentService
from extracto.utils.util import JsonResponse


logger = Logger()

document_api = APIRouter(tags=["Document Processing APIs"])


@document_api.get("")
async def list_of_documents():
    json_response = JsonResponse()
    try:
        print("Starting to list down the documents...")
        response = await DocumentService().list()
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "101", "message": f"Error in listing of documents: {e}"}
        print(f'Exception in listing of documents: {e}')
    return json_response.dict()


@document_api.post("")
async def upload_document(
        projectId: str = Form(),
        folderName: str = Form(),
        documentType: str = Form(),
        document: UploadFile = File(...)
):
    json_response = JsonResponse()
    try:
        response = await DocumentService().create(
            projectId=projectId, folderName=folderName,
            documentType=documentType, documentFile=document
        )
        print(f"Successfully uploaded document.")
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "102", "message": f"Error in uploading of document: {e}"}
        print(f'Exception in uploading document: {e}')
    return json_response.dict()


@document_api.get("/{documentId}")
async def get_document(documentId: str):
    json_response = JsonResponse()
    try:
        response = await DocumentService().get(documentId=documentId)
        print(f"Successfully retrieved the document with documentId: {documentId}.")
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "103", "message": f"Error in fetching the details of the document: {e}"}
        print(f'Exception in fetching the document: {e}')
    return json_response.dict()


@document_api.get("/{documentId}/download")
async def download_document(documentId: str):
    json_response = JsonResponse()
    try:
        response, filename = await DocumentService().download(documentId=documentId)
        print(f"Successfully retrieved the document with documentId: {documentId}.")
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "103", "message": f"Error in fetching the details of the document: {e}"}
        raise Exception(f'Exception in fetching the document: {e}')
    headers = {
        'Content-Disposition': f'inline; filename="{filename}"'
    }
    return Response(
        content=json_response.result,
        media_type="application/octet_stream",
        headers=headers,

    )
