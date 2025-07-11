from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models.user import User
from services import BalanceService


def test_home_request(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200


def test_sing_up_request(client: TestClient):
    response = client.post(
        "/user/signup",
        json={"login": 'test_user3', "password": "12344321"}
    )
    assert response.status_code == 200

def test_sing_up_bad_password(client: TestClient):
    response = client.post(
        "/user/signup",
        json={"login": 'test_user3', "password": "111"}
    )
    assert response.status_code != 200

def test_sing_up_bad_login(client: TestClient):
    response = client.post(
        "/user/signup",
        json={"login": 'test_user3±@^', "password": "12344321"}
    )
    assert response.status_code != 200

def test_sing_in_request(client: TestClient, user: User):
    response = client.post(
        "/user/signin",
        data={"username": 'test_user', "password": "12344321"}
    )
    assert response.status_code == 200
    assert response.json()['access_token']

def test_sing_in_request_bad_password(client: TestClient, user: User):
    try:
        response = client.post(
            "/user/signin",
            data={"username": 'test_user', "password": "123"}
        )
        assert False
    except Exception:
        assert True


def test_sing_in_request_bad_login(client: TestClient, user: User):
    try:
        response = client.post(
            "/user/signin",
            data={"username": 'test_user3±@^', "password": "12344321"}
        )
        assert False
    except Exception:
        assert True



def test_top_up_request(client: TestClient, user: User, session: Session):
    response = client.post(
        "/balance/top-up",
        json={"amount": 100}
    )
    session.refresh(user)
    assert response.status_code == 200
    assert user.balance == 100


def test_get_transaction_history_by_user_request(client: TestClient, user: User, session: Session):
    BalanceService.top_up_balance(user, 100, session)
    BalanceService.make_transaction(user, 10, "Оплата", session)

    response = client.get(
        "/balance/history/user",
    )

    session.refresh(user)
    assert response.status_code == 200
    assert user.balance == 90
    assert len(user.transactions) == 2
