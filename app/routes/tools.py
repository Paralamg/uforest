from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.user import User
from services import UserService


def get_user_by_login(login: str, session: Session) -> User:
    user_exist = UserService.get_user_by_login(login, session)

    if user_exist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    return user_exist


def check_user_exists(user: User, user_data_from_token: dict) -> None:
    if user is None or user.login != user_data_from_token["login"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
