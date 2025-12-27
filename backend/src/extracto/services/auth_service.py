import os
from datetime import datetime, timedelta

from fastapi import HTTPException, Request, Response

from extracto.db.azure.base import DBConnection
from extracto.db.model import User, RefreshToken
from extracto.logger.log_utils import Logger
from extracto.schema import schemas
from extracto.utils import auth_utils
from extracto.utils.util import get_current_datetime


logger = Logger()


class AuthService:
    def __init__(self):
        self.timestamp = get_current_datetime()
        self.cookie_name = os.getenv("COOKIE_NAME", "refresh_token")

    def set_refresh_cookie(self, response: Response, refresh_token: str):
        response.set_cookie(
            key=self.cookie_name,
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="Strict",
            path="/auth",
            max_age=auth_utils.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        )

    async def register(self, payload: schemas.UserCreate, response: Response):
        session = DBConnection().get_session()
        try:
            existing = session.query(User).filter(User.EMAIL == payload.email).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already registered")

            hashed_password = auth_utils.hash_password(payload.password)

            user = User(
                FIRST_NAME=payload.firstName,
                LAST_NAME=payload.lastName,
                EMAIL=payload.email,
                ROLE=payload.role,
                HASHED_PASSWORD=hashed_password,
                IS_ACTIVE=True,
                CREATED_AT=self.timestamp,
                MODIFIED_AT=self.timestamp
            )
            session.add(user)
            session.commit()
            session.refresh(user)

            # issue tokens
            access_token = auth_utils.create_access_token(str(user.ID))
            refresh_raw = auth_utils.create_refresh_token(str(user.ID))
            refresh_hash = auth_utils.hash_token(refresh_raw)
            expires_at = datetime.utcnow() + timedelta(days=auth_utils.REFRESH_TOKEN_EXPIRE_DAYS)

            db_token = RefreshToken(
                USER_ID=user.ID,
                TOKEN_HASH=refresh_hash,
                EXPIRED_AT=expires_at,
            )
            session.add(db_token)
            session.commit()

            # set cookie
            self.set_refresh_cookie(response, refresh_raw)

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.ID,
                    "username": user.EMAIL,
                    "role": user.ROLE,
                    "firstName": user.FIRST_NAME,
                    "lastName": user.LAST_NAME,
                    "created_at": user.CREATED_AT,
                    "modified_at": user.MODIFIED_AT
                  }
            }
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in register: {e}")
            raise
        finally:
            session.close()

    async def login(self, payload: schemas.LoginSchema, response: Response):
        session = DBConnection().get_session()
        try:
            user = session.query(User).filter(User.EMAIL == payload.email).first()
            if not user or not auth_utils.verify_password(payload.password, user.HASHED_PASSWORD):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            if not user.IS_ACTIVE:
                raise HTTPException(status_code=403, detail="Inactive user")

            access_token = auth_utils.create_access_token(str(user.ID))
            refresh_raw = auth_utils.create_refresh_token(str(user.ID))
            refresh_hash = auth_utils.hash_token(refresh_raw)
            expires_at = datetime.utcnow() + timedelta(days=auth_utils.REFRESH_TOKEN_EXPIRE_DAYS)

            db_token = RefreshToken(
                USER_ID=user.ID,
                TOKEN_HASH=refresh_hash,
                EXPIRED_AT=expires_at,
            )
            session.add(db_token)
            session.commit()

            self.set_refresh_cookie(response, refresh_raw)

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.ID,
                    "username": user.EMAIL,
                    "role": user.ROLE,
                    "firstName": user.FIRST_NAME,
                    "lastName": user.LAST_NAME,
                    "created_at": user.CREATED_AT,
                    "modified_at": user.MODIFIED_AT
                }
            }
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in login: {e}")
            raise
        finally:
            session.close()

    async def refresh(self, request: Request, response: Response):
        session = DBConnection().get_session()
        try:
            refresh_raw = request.cookies.get(self.cookie_name)
            if not refresh_raw:
                raise HTTPException(status_code=401, detail="Missing refresh cookie")

            refresh_hash = auth_utils.hash_token(refresh_raw)
            db_token = session.query(RefreshToken).filter(
                RefreshToken.TOKEN_HASH == refresh_hash,
                RefreshToken.REVOKED == False
            ).first()

            if not db_token:
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            if db_token.EXPIRED_AT < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Refresh token expired")

            # revoke old token
            db_token.REVOKED = True
            session.commit()

            # create new
            new_refresh_raw = auth_utils.create_refresh_token(str(db_token.USER_ID))
            new_refresh_hash = auth_utils.hash_token(new_refresh_raw)
            new_expires = datetime.utcnow() + timedelta(days=auth_utils.REFRESH_TOKEN_EXPIRE_DAYS)
            new_db_token = RefreshToken(
                USER_ID=db_token.USER_ID,
                TOKEN_HASH=new_refresh_hash,
                EXPIRED_AT=new_expires
            )
            session.add(new_db_token)
            session.commit()

            # new access token
            access_token = auth_utils.create_access_token(str(db_token.USER_ID))

            # set new cookie
            self.set_refresh_cookie(response, new_refresh_raw)

            return {"access_token": access_token, "token_type": "bearer"}
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in refresh: {e}")
            raise
        finally:
            session.close()

    async def logout(self, request: Request, response: Response):
        session = DBConnection().get_session()
        try:
            refresh_raw = request.cookies.get(self.cookie_name)
            if refresh_raw:
                refresh_hash = auth_utils.hash_token(refresh_raw)
                db_token = session.query(RefreshToken).filter(
                    RefreshToken.TOKEN_HASH == refresh_hash
                ).first()
                if db_token:
                    db_token.REVOKED = True
                    session.commit()

            response.delete_cookie(key=self.cookie_name, path="/auth")
            return {"ok": True}
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in logout: {e}")
            raise
        finally:
            session.close()

    def authenticate_user(self, email: str, password: str):
        """Verify a user's email and password against the DB."""
        session = DBConnection().get_session()
        try:
            user = session.query(User).filter(User.EMAIL == email).first()
            if not user:
                return None
            if not auth_utils.verify_password(password, user.HASHED_PASSWORD):
                return None
            access_token = auth_utils.create_access_token(user_id=str(user.ID))
            refresh_token = auth_utils.create_refresh_token(user_id=str(user.ID))
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.ID,
                    "username": user.EMAIL,
                    "role": user.ROLE,
                    "firstName": user.FIRST_NAME,
                    "lastName": user.LAST_NAME,
                    "created_at": user.CREATED_AT,
                    "modified_at": user.MODIFIED_AT
                }
            }
        except Exception as e:
            session.rollback()
            logger.error(f"Exception in refresh: {e}")
            raise
        finally:
            session.close()
