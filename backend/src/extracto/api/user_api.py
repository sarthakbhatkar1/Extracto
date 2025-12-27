from fastapi import APIRouter, UploadFile, File, Form, Depends

from extracto.logger.log_utils import Logger
from extracto.services.user_service import UserService
from extracto.utils.util import JsonResponse
from extracto.schema.objects import UserRequestModel
from extracto.db.model import User
from extracto.utils.user_dependancy import get_current_user,is_admin


logger = Logger()

user_api = APIRouter(tags=["User Management APIs"])


@user_api.get("")
async def list_of_users(user: User = Depends(is_admin)):
    json_response = JsonResponse()
    try:
        logger.info("Starting to list down the documents...")
        response = UserService(user=user).list()
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "101", "message": f"Error in listing of users: {e}"}
        logger.error(f'Exception in listing of users: {e}')
    return json_response.dict()


@user_api.post("")
async def create_user(
        userRequestModel: UserRequestModel,
        user: User = Depends(is_admin)
):
    json_response = JsonResponse()
    try:
        response = UserService(user=user).create(
            userName=userRequestModel.userName,
            name=userRequestModel.name,
            emailId=userRequestModel.emailId,
            password=userRequestModel.password
        )
        logger.info(f"Successfully uploaded document.")
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "102", "message": f"Error in uploading of document: {e}"}
        logger.error(f'Exception in uploading document: {e}')
    return json_response.dict()


@user_api.get("/{userId}")
async def fetch_user(userId: str, user: User = Depends(is_admin)):
    json_response = JsonResponse()
    try:
        response = UserService(user=user).get(userId=userId)
        logger.info(f"Successfully retrieved the document with userId: {userId}.")
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "103", "message": f"Error in fetching the details of the document: {e}"}
        logger.error(f'Exception in fetching the document: {e}')
    return json_response.dict()


@user_api.post("/{userId}")
async def update_user(userId: str, user: User = Depends(is_admin)):
    json_response = JsonResponse()
    try:
        response = UserService(user=user).update(userId=userId)
        logger.info(f"Successfully retrieved the document with userId: {userId}.")
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "103", "message": f"Error in fetching the details of the document: {e}"}
        logger.error(f'Exception in fetching the document: {e}')
    return json_response.dict()


@user_api.post("/{userId}")
async def delete_user(userId: str, user: User = Depends(is_admin)):
    json_response = JsonResponse()
    try:
        response = UserService(user=user).delete(userId=userId)
        logger.info(f"Successfully retrieved the document with userId: {userId}.")
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "103", "message": f"Error in fetching the details of the document: {e}"}
        logger.error(f'Exception in fetching the document: {e}')
    return json_response.dict()
