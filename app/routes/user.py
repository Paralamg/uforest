from fastapi import APIRouter, Depends, HTTPException, status

from auth.authenticate import authenticate
from auth.jwt_handler import create_access_token
from database.database import get_session
from sqlalchemy.orm import Session
from models.schemas import UserSchema, TokenResponse
from routes.tools import check_user_exists
from services import UserService
from auth.hash_password import HashPassword
from fastapi.security import OAuth2PasswordRequestForm

from services.logger import get_logger

user_route = APIRouter(tags=["user"])
hash_password = HashPassword()
logging = get_logger(logger_name=__name__)

@user_route.post("/signup")
async def sing_up(user: UserSchema, session: Session = Depends(get_session)):
    user_exist = UserService.get_user_by_login(user.login, session)

    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with supplied username exists")

    UserService.create_user(user, session)

    return {"message": "User successfully registered!"}


@user_route.post("/signin", response_model=TokenResponse)
async def sing_in(user: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user_data = UserSchema(login=user.username, password=user.password)

    # Проверяем, существует ли пользователь
    user_exist = UserService.get_user_by_login(user_data.login, session)

    if user_exist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    p = hash_password.create_hash(user.password)
    if hash_password.verify_hash(user.password, user_exist.password_hash):
        access_token = create_access_token(user_exist)
        logging.info(f"Пользователь {user_exist.login}: успешный вход")
        return {"access_token": access_token, "token_type": "Bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid details passed."
    )


@user_route.get("/balance")
async def get_balance(
        user: dict = Depends(authenticate),
        session: Session = Depends(get_session)
):
    user_db = UserService.get_user_by_id(user["id"], session)
    check_user_exists(user_db, user)
    return {"balance": user_db.balance}
