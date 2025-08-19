import logging

from extracto.db.base import DBConnection
from extracto.db.model import Task

logger = logging.getLogger(__name__)


class TaskService:

    def __init__(self):
        pass

    def list(self):
        response = []
        session = DBConnection().get_session()
        try:
            projects: [Task] = session.query(Task).all()
            for project in projects:
                response.append(self.response())
        except Exception as e:
            logger.error(f"Exception in task listing: {e}")
            raise Exception(e)
        finally:
            session.close()

    def create(self):
        pass

    def get(self):
        pass

    def response(self, task: Task):
        return TaskResponse(
            taskId=task.ID
        )