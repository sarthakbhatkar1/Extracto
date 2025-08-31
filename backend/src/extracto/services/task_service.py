import logging

from extracto.db.azure.base import DBConnection
from extracto.db.model import Task
from extracto.schema.objects import TaskRequestSchema
from extracto.schema.response import TaskResponse
from extracto.logger.log_utils import Logger

logger = Logger()


class TaskService:

    def __init__(self):
        pass

    def list(self):
        response = []
        session = DBConnection().get_session()
        try:
            projects: [Task] = session.query(Task).all()
            for project in projects:
                response.append(self.response(project))
        except Exception as e:
            logger.error(f"Exception in task listing: {e}")
            raise Exception(e)
        finally:
            session.close()
        return response

    def create(self, taskRequestSchema: TaskRequestSchema):
        response = []
        session = DBConnection().get_session()
        try:
            projects: [Task] = session.query(Task).all()
            for project in projects:
                response.append(self.response(project))
        except Exception as e:
            logger.error(f"Exception in task listing: {e}")
            raise Exception(e)
        finally:
            session.close()
        return response

    def get(self, taskId: str):
        response = []
        session = DBConnection().get_session()
        try:
            projects: [Task] = session.query(Task).all()
            for project in projects:
                response.append(self.response(project))
        except Exception as e:
            logger.error(f"Exception in task listing: {e}")
            raise Exception(e)
        finally:
            session.close()
        return response

    def response(self, task: Task):
        return TaskResponse(
            taskId=task.ID,
            output=task.OUTPUT,
            createdTs=task.CREATED_TS,
            modifiedts=task.MODIFIED_TS
        )