from sqlalchemy.orm import Session

from auth.hash_password import HashPassword
from models.schemas import UserSchema
from models.user import User
from services.logger import get_logger

logging = get_logger(logger_name=__name__)


class UserService:
    @staticmethod
    def create_user(user_data: UserSchema, session: Session) -> int:
        """
        Create a new user
        :param user_data: information about the new user (username, password, is_admin)
        :param session: sqlalchemy's database session
        :return: user id
        """
        password_hash = HashPassword.create_hash(user_data.password)
        user = User(
            login=user_data.login,
            password_hash=password_hash,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        logging.info(f"Пользователь {user.login}: создан")
        return user.id

    @staticmethod
    def get_user_by_login(login: str, session: Session) -> User | None:
        """
        Get user by login from database
        :param login: login of the user
        :param session: sqlalchemy's database session
        :return: user object
        """
        user = session.query(User).filter(User.login == login).first()
        if user:
            return user
        return None

    @staticmethod
    def get_user_by_id(user_id: int, session: Session) -> User | None:
        """
        Get user by id from database
        :param user_id: id of the user
        :param session: sqlalchemy's database session
        :return: user object
        """
        user = session.get(User, user_id)
        if user:
            return user
        return None
