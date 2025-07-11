import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from api import app
from auth.authenticate import authenticate
from auth.hash_password import HashPassword
from database.database import Base, get_session
from models.user import User


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///testing.db", connect_args={"check_same_thread": False})
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(engine)
    with session_factory() as session:
        yield session


@pytest.fixture(name="user")
def user_fixture(session: Session):
    user = User(id=1, login="test_user", password_hash=HashPassword.create_hash("12344321"), balance=0)
    session.add(user)
    session.commit()
    return user


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[authenticate] = lambda: {"id": 1, "login": "test_user"}

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
