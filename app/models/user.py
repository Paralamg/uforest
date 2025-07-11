import datetime
import enum
from typing import Annotated

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base, intpk, created_at, updated_at


class User(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    login: Mapped[str]
    password_hash: Mapped[str]
    balance: Mapped[int] = mapped_column(default=0)
    is_admin: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[created_at]

    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="user"
    )

    predictions: Mapped[list["Prediction"]] = relationship(
        back_populates="user"
    )


class TransactionType(enum.Enum):
    deposit = 0
    withdraw = 1


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    amount: Mapped[int]
    description: Mapped[str | None]
    type: Mapped[TransactionType]
    created_at: Mapped[created_at]

    user: Mapped["User"] = relationship(
        back_populates="transactions"
    )


class Prediction(Base):
    __tablename__ = 'predictions'

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    task_id: Mapped[str]
    task_status: Mapped[str]
    input_data: Mapped[str]
    cost: Mapped[int]
    prediction: Mapped[str | None]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user: Mapped["User"] = relationship(
        back_populates="predictions"
    )
