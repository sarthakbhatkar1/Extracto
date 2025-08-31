import logging
from fastapi import APIRouter

from extracto.services.task_service import TaskService
from extracto.utils.util import JsonResponse
from extracto.schema.objects import TaskRequestSchema

task_api = APIRouter(tags=["Task Management APIs"])

logger = logging.getLogger(__name__)


@task_api.get("")
async def list():
    json_response = JsonResponse()
    try:
        response = TaskService().list()
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "101", "message": f"Error in listing of tasks: {e}"}
    return json_response.dict()


@task_api.post("")
async def create(taskRequestSchema: TaskRequestSchema):
    json_response = JsonResponse()
    try:
        response = TaskService().create(
            taskRequestSchema=taskRequestSchema
        )
        print(f"Successfully uploaded task.")
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "101", "message": f"Error in creating a task: {e}"}
    return json_response.dict()


@task_api.get("/{taskId}")
async def get(taskId: str):
    json_response = JsonResponse()
    try:
        response = TaskService().get(taskId=taskId)
        print(f"Successfully retrieved the task with taskId: {taskId}.")
        json_response.result = response
        json_response.success = True
    except Exception as e:
        json_response.error = {"code": "102", "message": f"Error in fetching the details of the task: {e}"}
    return json_response.dict()
