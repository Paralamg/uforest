from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.authenticate import authenticate
from database.database import get_session
from models.schemas import TopUpScheme
from routes.tools import check_user_exists
from services import BalanceService, UserService

balance_route = APIRouter(tags=["balance"])


@balance_route.post("/top-up")
async def top_up_balance(data: TopUpScheme,
                         user: dict = Depends(authenticate),
                         session: Session = Depends(get_session),
                         ):
    user_db = UserService.get_user_by_id(user["id"], session)
    check_user_exists(user_db, user)

    if user_db is None or user_db.login != user["login"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    BalanceService.top_up_balance(user_db, data.amount, session)
    return {"message": "Successful top up!"}


@balance_route.get("/history", response_model=List[dict])
async def get_transaction_history(
        user: dict = Depends(authenticate),
        session: Session = Depends(get_session)
):
    # TODO: Права админа
    transactions = BalanceService.get_transactions_history(session)
    return [
        {
            "id": transaction.id,
            "user_id": transaction.user_id,
            "amount": transaction.amount,
            "description": transaction.description,
            "type": transaction.type,
            "created_at": transaction.created_at.isoformat(),
        }
        for transaction in transactions
    ]


@balance_route.get("/history/user", response_model=List[dict])
async def get_transaction_history_by_user(
        user: dict = Depends(authenticate),
        session: Session = Depends(get_session)
):
    user_db = UserService.get_user_by_id(user["id"], session)
    check_user_exists(user_db, user)

    transactions = BalanceService.get_prediction_history_by_user(user_db, session)
    return [
        {
            "id": transaction.id,
            "amount": transaction.amount,
            "description": transaction.description,
            "type": transaction.type,
            "created_at": transaction.created_at.isoformat(),
        }
        for transaction in transactions
    ]
