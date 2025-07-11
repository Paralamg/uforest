from sqlalchemy.orm import Session

from models.user import User
from services import BalanceService


def test_create_user(session: Session):
    try:
        user = User(id=2, login="test_user2", password_hash="123", balance=0)
        session.add(user)
        session.commit()
        assert True
    except:
        assert False


def test_top_up(session: Session, user: User):
    try:
        BalanceService.top_up_balance(user, 100, session)
        session.refresh(user)
        assert True
        assert user.balance == 100
        assert user.transactions
    except:
        assert False


def test_make_transaction(session: Session, user: User):
    try:
        BalanceService.make_transaction(user, 10, "Оплата", session)
        session.refresh(user)
        assert True
        assert user.balance == -10
        assert user.transactions
    except:
        assert False
