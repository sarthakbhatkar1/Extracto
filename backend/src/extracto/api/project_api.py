from fastapi import APIRouter, Depends

from extracto.db.model import User
from extracto.schema.objects import ProjectRequestSchema
from extracto.services.project_service import ProjectService
from extracto.utils.user_dependancy import get_current_user
from extracto.utils.util import JsonResponse

project_api = APIRouter(tags=["Project Management APIs"])


@project_api.get("")
async def list(user: User = Depends(get_current_user)):
    json_response = JsonResponse()
    try:
        response = await ProjectService(user=user).list()
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "101", "message": f"Error in listing of projects: {e}"}
    return json_response.dict()


@project_api.get("/{projectId}/documents")
async def list_by_project(projectId: str, user: User = Depends(get_current_user)):
    json_response = JsonResponse()
    try:
        response = await ProjectService(user=user).list_based_on_project(projectId=projectId)
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "101", "message": f"Error in listing of projects: {e}"}
    return json_response.dict()


@project_api.post("")
async def create(projectRequestSchema: ProjectRequestSchema, user: User = Depends(get_current_user)):
    json_response = JsonResponse()
    try:
        response = await ProjectService(user=user).create(
            projectName=projectRequestSchema.projectName,
            tags=projectRequestSchema.tags,
            description=projectRequestSchema.description,
            workflow=projectRequestSchema.workflow
        )
        print(f"Successfully uploaded project.")
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "101", "message": f"Error in creating a project: {e}"}
    return json_response.dict()


@project_api.get("/{project_id}")
async def get(projectId: str, user: User = Depends(get_current_user)):
    json_response = JsonResponse()
    try:
        response = await ProjectService(user=user).get(projectId=projectId)
        print(f"Successfully retrieved the project with projectId: {projectId}.")
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "102", "message": f"Error in fetching the details of the project: {e}"}
    return json_response.dict()


@project_api.post("/{project_id}")
async def update(projectId: str, projectRequestSchema: ProjectRequestSchema, user: User = Depends(get_current_user)):
    json_response = JsonResponse()
    try:
        response = await ProjectService(user=user).update(
            projectId=projectId,
            projectName=projectRequestSchema.projectName,
            tags=projectRequestSchema.tags,
            description=projectRequestSchema.description,
            workflow=projectRequestSchema.workflow
        )
        print(f"Successfully retrieved the project with project_id: {projectId}.")
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "103", "message": f"Error in updating the details of the project: {e}"}
    return json_response.dict()


@project_api.post("/{project_id}/delete")
async def delete(projectId: str, user: User = Depends(get_current_user)):
    json_response = JsonResponse()
    try:
        response = await ProjectService(user=user).delete(projectId=projectId)
        print(f"Successfully retrieved the project with projectId: {projectId}.")
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "104", "message": f"Error in deleting the the project: {e}"}
    return json_response.dict()
