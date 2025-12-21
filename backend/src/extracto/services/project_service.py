import logging
from typing import List

from extracto.db.azure.base import DBConnection
from extracto.schema.objects import ProjectWorkflow
from extracto.db.model import Document, Project, User
from extracto.schema.response import ProjectResponse, DocumentResponse
from extracto.utils.util import get_unique_number, get_current_datetime

logger = logging.getLogger(__name__)


class ProjectService:

    def __init__(self, user: User):
        self.user = user
        self.created_at = get_current_datetime()
        self.modified_at = get_current_datetime()

    async def list(self):
        response = []
        session = DBConnection().get_session()
        try:
            projects: [Project] = session.query(Project).filter(
                Project.OWNER == self.user.ID).all()
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

    async def list_based_on_project(self, projectId: str):
        """
        Fetch documents grouped by project and folder.
        - If user is Admin → fetch all projects/documents.
        - Else → fetch only projects owned by the logged-in user.
        """
        session = DBConnection().get_session()
        response = {}
        try:
            logger.info(f"Fetching documents for user {self.user.ID} with role {self.user.ROLE}...")

            # Check if user is admin
            if self.user.ROLE and self.user.ROLE.lower() == "admin":
                projects = session.query(Project).all()
            else:
                if projectId:
                    projects = (session.query(Project).filter(Project.OWNER == self.user.ID).filter
                                    (Project.ID == projectId).all())
                else:
                    projects = session.query(Project).filter(Project.OWNER == self.user.ID).all()

            for project in projects:
                project_entry = {
                    "projectId": str(project.ID),
                    "projectName": project.NAME,
                    "folders": {}
                }

                # Fetch documents under this project
                documents = (
                    session.query(Document)
                    .filter(Document.PROJECT_ID == project.ID)
                    .all()
                )

                for doc in documents:
                    folder_name = doc.FOLDER_NAME or "root"

                    if folder_name not in project_entry["folders"]:
                        project_entry["folders"][folder_name] = []

                    project_entry["folders"][folder_name].append(self.document_response(document=doc))

                # Convert dict → list for folders
                project_entry["folders"] = [
                    {
                        "folderName": fname,
                        "documents": docs
                    } for fname, docs in project_entry["folders"].items()
                ]

                response = project_entry

            logger.info("Successfully fetched grouped documents.")

        except Exception as e:
            session.rollback()
            logger.error(f"Exception in listing documents: {e}")
            raise Exception(f"Exception in listing documents: {e}")
        finally:
            session.commit()
            session.close()

        return response

    async def create(self, projectName: str, tags: List, description: str, workflow: [ProjectWorkflow] = None):
        response = {}
        session = DBConnection().get_session()
        projectId = get_unique_number()
        project_workflow = []
        try:
            is_project_name_exists: Project = session.query(Project).filter(
                Project.OWNER == self.user.ID
            ).filter(Project.NAME == projectName).first()
            if is_project_name_exists:
                logger.error(f"Project '{projectName} already exists. Please provide an unique name.")
                raise Exception(f"Project '{projectName} already exists. Please provide an unique name.")

            if workflow:
                project_workflow = [_workflow.dict() for _workflow in workflow]
            project: Project = Project(
                ID=projectId,
                NAME=projectName,
                TAGS=tags,
                DESCRIPTION=description,
                WORKFLOW=project_workflow,
                OWNER=self.user.ID,
                CREATED_AT=self.created_at,
                MODIFIED_AT=self.modified_at
            )
            session.add(project)
            session.commit()
            response = self.response(project=project)
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in creating projects: {e}")
            raise Exception(f"Exception in creating projects: {e}")
        finally:
            session.close()
        logger.info(f"Project '{projectName} created successfully.'")
        return response

    async def get(self, projectId: str):
        response = {}
        session = DBConnection().get_session()
        try:
            project: Project = session.query(Project).filter(
                Project.OWNER == self.user.ID
            ).filter(Project.ID == projectId).first()
            if not project:
                logger.error(f"Project with projectId'{projectId} already exists. Please provide a valid projectId.")
                raise Exception(f"Project '{projectId} already exists. Please provide a valid projectId.")
            session.commit()
            session.refresh(project)
            response = self.response(project=project)
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in listing projects: {e}")
            raise Exception(f"Exception in listing projects: {e}")
        finally:
            session.close()
        logger.info(f"Project '{projectId} fetched successfully.'")
        return response

    async def update(self, projectId: str, projectName: str = None, tags: List = None, description: str = None, workflow: [ProjectWorkflow] = None):
        response = {}
        session = DBConnection().get_session()
        update_dict = {}
        try:
            if projectName:
                update_dict[Project.NAME] = projectName
            if tags:
                update_dict[Project.TAGS] = tags
            if description:
                update_dict[Project.DESCRIPTION] = description
            if workflow:
                update_dict[Project.WORKFLOW]= workflow
            is_project_updated = session.query(Project).filter(
                Project.OWNER == self.user.ID
            ).filter(Project.ID == projectId).update(update_dict)
            if not is_project_updated:
                logger.error(f"Error in updating the project with projectId - {projectId}.")
                raise Exception(f"Error in updating the project with projectId - {projectId}.")
            session.commit()
            response = await self.get(projectId=projectId)
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in listing projects: {e}")
            raise Exception(f"Exception in listing projects: {e}")
        finally:
            session.close()
        logger.info(f"Project '{projectId} deleted successfully.'")
        return response

    async def delete(self, projectId: str):
        response = {}
        session = DBConnection().get_session()
        try:
            response = await self.get(projectId=projectId)
            is_project_deleted = session.query(Project).filter(
                Project.OWNER == self.user.ID).filter(Project.ID == projectId).delete()
            if not is_project_deleted:
                logger.error(f"Error in deleting the project with projectId - {projectId}.")
                raise Exception(f"Error in deleting the project with projectId - {projectId}.")
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in listing projects: {e}")
            raise Exception(f"Exception in listing projects: {e}")
        finally:
            session.close()
        logger.info(f"Project '{projectId} deleted successfully.'")
        return response

    def response(self, project: Project):
        return ProjectResponse(
            projectId=project.ID,
            projectName=project.NAME,
            tags=project.TAGS,
            description=project.DESCRIPTION,
            owner=project.OWNER,
            createdTs=project.CREATED_AT,
            modifiedTs=project.MODIFIED_AT
        ).dict()

    def document_response(self, document: Document):
        return DocumentResponse(
            projectId=document.PROJECT_ID,
            folderName=document.FOLDER_NAME,
            documentId=document.ID,
            documentName=document.NAME,
            storagePath=document.STORAGE_PATH,
            createdTs=document.CREATED_AT,
            modifiedTs=document.MODIFIED_AT
        )