from sqlalchemy import String

from extracto.db.azure.base import DBConnection
from extracto.db.model import Document, Project, Task, User
from extracto.logger.log_utils import Logger
from extracto.schema.objects import TaskRequestSchema
from extracto.schema.response import TaskResponse
from extracto.utils.util import get_current_datetime
from extracto.schema.enums import TaskStatus

logger = Logger()


class TaskService:

    def __init__(self, user: User):
        self.user = user
        self.created_at = get_current_datetime()
        self.modified_at = get_current_datetime()

    def list(self):
        response = []
        session = DBConnection().get_session()
        try:
            tasks: [Task] = session.query(Task).all()
            for task in tasks:
                response.append(self.response(task))
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in task listing: {e}")
            raise Exception(e)
        finally:
            session.close()
        return response

    def list_tasks_by_user(self):
        """
        Fetch all tasks triggered by a specific user through project ownership
        Since tasks don't have direct user ownership, we trace through:
        Task -> Document -> Project -> User

        Args:
            user_id (UUID): The UUID of the user

        Returns:
            list: List of tasks from projects owned by the user
        """
        response = None
        session = DBConnection().get_session()
        try:
            # Query tasks through the project ownership chain
            tasks = session.query(Task) \
                .join(Document, Task.DOCUMENT_IDS.contains([Document.ID.cast(String)])) \
                .join(Project, Document.PROJECT_ID == Project.ID) \
                .filter(Project.OWNER == self.user.ID) \
                .all()

            # for task in tasks:
            #     response.append(self.response(task))
            response = [self.response(task) for task in tasks]
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in user task listing: {e}")
            raise Exception(e)
        finally:
            session.close()
        return response

    def create(self, taskRequestSchema: TaskRequestSchema):
        response = None
        session = DBConnection().get_session()
        try:
            task: Task = Task(
                DOCUMENT_IDS=taskRequestSchema.documentIds,
                STATUS=TaskStatus.NOT_STARTED,
                CREATED_AT=self.created_at,
                MODIFIED_AT=self.modified_at
            )
            session.add(task)
            session.commit()
            response = self.response(task=task)
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in task listing: {e}")
            raise Exception(e)
        finally:
            session.close()
        return response

    def get(self, taskId: str):
        response = None
        session = DBConnection().get_session()
        try:
            task: Task = session.query(Task).filter(Task.ID == taskId).first()
            response = self.response(task=task)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in task listing: {e}")
            raise Exception(e)
        finally:
            session.close()
        return response

    def response(self, task: Task):
        return TaskResponse(
            taskId=task.ID,
            status=task.STATUS,
            output=task.OUTPUT,
            createdTs=task.CREATED_AT,
            modifiedTs=task.MODIFIED_AT
        )