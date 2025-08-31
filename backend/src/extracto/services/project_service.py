import logging
from typing import List

from extracto.db.azure.base import DBConnection
from extracto.schema.objects import ProjectWorkflow
from extracto.db.model import Project
from extracto.schema.response import ProjectResponse
from extracto.utils.util import get_unique_number, get_current_datetime

logger = logging.getLogger(__name__)


class ProjectService:

    def __init__(self):
        self.created_ts = get_current_datetime()
        self.modified_ts = get_current_datetime()

    async def list(self):
        response = []
        session = DBConnection().get_session()
        try:
            projects: [Project] = session.query(Project).all()
            for project in projects:
                _project = self.response(project=project)
                response.append(_project)
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in listing projects: {e}")
            raise Exception(f"Exception in listing projects: {e}")
        finally:
            session.commit()
            session.close()
        logger.info(f"Successfully fetched the list of projects.")
        return response

    async def create(self, projectName: str, tags: List, description: str, workflow: [ProjectWorkflow] = []):
        response = {}
        session = DBConnection().get_session()
        project_id = get_unique_number()
        try:
            is_project_name_exists: Project = session.query(Project).filter(Project.NAME == projectName).first()
            if is_project_name_exists:
                logger.error(f"Project '{projectName} already exists. Please provide an unique name.")
                raise Exception(f"Project '{projectName} already exists. Please provide an unique name.")

            import pdb; pdb.set_trace()
            project_workflow = [_workflow.dict() for _workflow in workflow]
            project: Project = Project(
                ID=project_id,
                NAME=projectName,
                TAGS=tags,
                DESCRIPTION=description,
                WORKFLOW=project_workflow,
                CREATED_TS=self.created_ts,
                MODIFIED_TS=self.modified_ts
            )
            session.add(project)
            response = self.response(project=project)
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in listing projects: {e}")
            raise Exception(f"Exception in listing projects: {e}")
        finally:
            session.commit()
            session.close()
        logger.info(f"Project '{projectName} created successfully.'")
        return response

    async def get(self, project_id: str):
        response = {}
        session = DBConnection().get_session()
        try:
            project: Project = session.query(Project).filter(Project.ID == project_id).first()
            if not project:
                logger.error(f"Project with project_id'{project_id} already exists. Please provide a valid project_id.")
                raise Exception(f"Project '{project_id} already exists. Please provide a valid project_id.")
            response = self.response(project=project)
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in listing projects: {e}")
            raise Exception(f"Exception in listing projects: {e}")
        finally:
            session.commit()
            session.close()
        logger.info(f"Project '{project_id} fetched successfully.'")
        return response

    async def update(self, project_id: str, projectName: str, tags: List, description: str, workflow: [ProjectWorkflow] = []):
        response = {}
        session = DBConnection().get_session()
        try:
            response = await self.get(project_id=project_id)
            is_project_deleted = session.query(Project).filter(Project.ID == project_id).delete()
            if not is_project_deleted:
                logger.error(f"Error in deleting the project with project_id - {project_id}.")
                raise Exception(f"Error in deleting the project with project_id - {project_id}.")
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in listing projects: {e}")
            raise Exception(f"Exception in listing projects: {e}")
        finally:
            session.commit()
            session.close()
        logger.info(f"Project '{project_id} deleted successfully.'")
        return response

    async def delete(self, project_id: str):
        response = {}
        session = DBConnection().get_session()
        try:
            response = await self.get(project_id=project_id)
            is_project_deleted = session.query(Project).filter(Project.ID == project_id).delete()
            if not is_project_deleted:
                logger.error(f"Error in deleting the project with project_id - {project_id}.")
                raise Exception(f"Error in deleting the project with project_id - {project_id}.")
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in listing projects: {e}")
            raise Exception(f"Exception in listing projects: {e}")
        finally:
            session.commit()
            session.close()
        logger.info(f"Project '{project_id} deleted successfully.'")
        return response

    def response(self, project: Project):
        return ProjectResponse(
            projectId=project.ID,
            projectName=project.NAME,
            tags=project.TAGS,
            description=project.DESCRIPTION,
            createdTs=project.CREATED_TS,
            modifiedTs=project.MODIFIED_TS
        ).dict()
