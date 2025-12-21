from extracto.logger.log_utils import Logger
from extracto.utils.util import get_unique_number
from extracto.db.model import User
from extracto.schema.response import UserResponse
from extracto.db.supabase.base import DBConnection
from extracto.utils.util import get_current_datetime, RoleEnum

logger = Logger()


class UserService:

    def __init__(self, user: User):
        self.user = user
        self.created_at = get_current_datetime()
        self.modified_at = get_current_datetime()

    def list(self):
        response = []
        session = DBConnection().get_session()
        try:
            logger.info(f"Fetching the documents from the database.")
            users: list[User] = session.query(User).all()
            logger.info(f"Successfully fetched the documents from the database.")
            for user in users:
                response.append(self.response(user=user))
        except Exception as e:
            logger.error(f"Exception in listing users: {e}")
            raise Exception(f"Exception in listing users: {e}")
        finally:
            session.commit()
            session.close()
        logger.info("Starting to list down the documents...")
        return response

    def create(self, userName: str, name: str, emailId: str, password: str, role: str = RoleEnum.USER):
        response = None
        userId = get_unique_number()
        session = DBConnection().get_session()
        try:
            user: User = User(
                ID=userId,
                NAME=name,
                USERNAME=userName,
                EMAIL=emailId,
                PASSWORD=password,
                ROLE=role,
                CREATED_AT=self.created_at,
                MODIFIED_AT=self.modified_at
            )
            session.add(user)
            response = self.response(user=user)
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in creating a new user: {e}")
            raise Exception(f"Exception in creating a new user: {e}")
        finally:
            session.commit()
            session.close()
        return response

    def get(self, userId: str):
        response = None
        session = DBConnection().get_session()
        try:
            user: User = session.query(User).filter(User.ID == userId).first()
            response = self.response(user=user)
        except Exception as e:
            print(f"Exception in fetching the user details: {e}")
            raise Exception(f"Exception in fetching the user details: {e}")
        finally:
            session.commit()
            session.close()
        return response

    async def update(self, userId: str, userName: str, name: str, emailId: str, password: str, role: str = RoleEnum.USER):
        response = {}
        session = DBConnection().get_session()
        try:
            response = await self.get(userId=userId)
            is_project_deleted = session.query(User).filter(User.ID == userId).delete()
            if not is_project_deleted:
                logger.error(f"Error in updating the user with userId - {userId}.")
                raise Exception(f"Error in updating the user with userId - {userId}.")
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in listing projects: {e}")
            raise Exception(f"Exception in listing projects: {e}")
        finally:
            session.commit()
            session.close()
        logger.info(f"User id '{userId} deleted successfully.'")
        return response

    async def delete(self, userId: str):
        response = None
        session = DBConnection().get_session()
        try:

            user: User = session.query(User).filter(User.ID == userId).delete()
            response = self.response(user=user)
        except Exception as e:
            print(f"Exception in deleting the user: {e}")
            raise Exception(f"Exception in deleting the user: {e}")
        finally:
            session.commit()
            session.close()
        return response

    def response(self, user: User):
        return UserResponse(
            userId=user.ID,
            userName=user.USERNAME,
            name=user.NAME,
            email=user.EMAIL,
            role=user.ROLE,
            createdTs=user.CREATED_AT,
            modifiedTs=user.MODIFIED_AT
        )
