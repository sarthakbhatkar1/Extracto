from datetime import datetime
from sqlalchemy.orm import Session

from daemon.db.model import Task, Project, WorkflowConfig
from daemon.constants.enums import TaskStatus


class TaskRepository:

    @staticmethod
    def fetch_next_task(session: Session) -> Task | None:
        return (
            session.query(Task)
            .filter(Task.STATUS["status"].astext == TaskStatus.NOT_STARTED.value)
            .order_by(Task.CREATED_AT)
            .first()
        )

    @staticmethod
    def mark_in_progress(session: Session, task: Task):
        task.STATUS["status"] = TaskStatus.IN_PROGRESS.value
        task.MODIFIED_AT = datetime.utcnow()
        session.commit()

    @staticmethod
    def mark_success(session: Session, task: Task):
        task.STATUS["status"] = TaskStatus.SUCCESS.value
        task.MODIFIED_AT = datetime.utcnow()
        session.commit()

    @staticmethod
    def mark_failure(session: Session, task: Task):
        task.STATUS["status"] = TaskStatus.FAILURE.value
        task.MODIFIED_AT = datetime.utcnow()
        session.commit()

    @staticmethod
    def get_project_workflow(session: Session, task: Task) -> dict:
        document_id = task.DOCUMENT_IDS[0]

        project = (
            session.query(Project)
            .join(Project.documents)
            .filter_by(ID=document_id)
            .first()
        )

        if not project or not project.WORKFLOW:
            raise ValueError("No workflow defined for project")

        return project.WORKFLOW
