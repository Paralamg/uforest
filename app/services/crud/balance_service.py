from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.user import User, Transaction, TransactionType
from services.logger import get_logger

logging = get_logger(logger_name=__name__)


class BalanceService:
    @staticmethod
    def top_up_balance(user: User, amount: int, session: Session):
        user.balance += amount
        description = "Top up balance"
        transaction = Transaction(
            user_id=user.id,
            amount=amount,
            description=description,
            type=TransactionType.deposit
        )
        session.add(transaction)
        session.commit()
        logging.info(f"Пользователь {user.login}: пополнил баланс на {amount} монет")

    @staticmethod
    def make_transaction(user: User, amount: int, description: str, session: Session):
        user.balance -= amount
        transaction = Transaction(
            user_id=user.id,
            amount=amount,
            description=description,
            type=TransactionType.withdraw
        )
        session.add(transaction)
        session.commit()
        logging.info(f"Пользователь {user.login}: сделал транзакцию на {amount} монет. Описание: {description}")

    @staticmethod
    def get_transactions_history(session: Session) -> Sequence[Transaction]:
        query = select(Transaction)
        result = session.execute(query)
        transactions = result.scalars().all()
        return transactions

    @staticmethod
    def get_prediction_history_by_user(user: User, session: Session) -> Sequence[Transaction]:
        query = select(Transaction).filter(user.id == Transaction.user_id)
        result = session.execute(query)
        transactions = result.scalars().all()
        logging.info(f"Пользователь {user.login}: сделал запрос на получение истории транзакций")
        return transactions
