from fastapi import APIRouter, UploadFile, File, Form
from typing import List

from extracto.schema.project_schema import ProjectWorkflow
from extracto.services.project_service import ProjectService
from extracto.utils.util import JsonResponse
from extracto.schema.project_schema import ProjectRequestSchema

project_api = APIRouter(tags=["Project Management APIs"])


@project_api.get("")
async def list():
    json_response = JsonResponse()
    try:
        response = await ProjectService().list()
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "101", "message": f"Error in listing of projects: {e}"}
    return json_response.dict()


@project_api.post("")
async def create(projectRequestSchema: ProjectRequestSchema):
    json_response = JsonResponse()
    try:
        response = await ProjectService().create(
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
async def get(project_id: str):
    json_response = JsonResponse()
    try:
        response = await ProjectService().get(project_id=project_id)
        print(f"Successfully retrieved the project with project_id: {project_id}.")
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "102", "message": f"Error in fetching the details of the project: {e}"}
    return json_response.dict()


@project_api.post("/{project_id}")
async def update(project_id: str, projectRequestSchema: ProjectRequestSchema):
    json_response = JsonResponse()
    try:
        response = await ProjectService().update(
            project_id=project_id,
            projectName=projectRequestSchema.projectName,
            tags=projectRequestSchema.tags,
            description=projectRequestSchema.description,
            workflow=projectRequestSchema.workflow
        )
        print(f"Successfully retrieved the project with project_id: {project_id}.")
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "103", "message": f"Error in updating the details of the project: {e}"}
    return json_response.dict()


@project_api.post("/{project_id}/delete")
async def delete(project_id: str):
    json_response = JsonResponse()
    try:
        response = await ProjectService().delete(project_id=project_id)
        print(f"Successfully retrieved the project with project_id: {project_id}.")
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "104", "message": f"Error in deleting the the project: {e}"}
    return json_response.dict()
