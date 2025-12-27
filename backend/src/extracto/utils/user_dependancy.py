from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from extracto.db.azure.base import DBConnection
from extracto.db.model import User
from extracto.logger.log_utils import Logger
from extracto.utils import auth_utils
from extracto.utils.util import RoleEnum

logger = Logger()


def get_session():
    return DBConnection().get_session()


def get_current_user(token: str = Depends(auth_utils.oauth2_scheme), session: Session = Depends(get_session)):
    user_id = auth_utils.decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = session.query(User).filter(User.ID == str(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.IS_ACTIVE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    return user


def is_admin(token: str = Depends(auth_utils.oauth2_scheme), session: Session = Depends(get_session)):
    user_id = auth_utils.decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = session.query(User).filter(User.ID == str(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.IS_ACTIVE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    if user.ROLE != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admins have access to user functionality."
        )

    return user

