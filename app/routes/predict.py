import base64
from contextlib import asynccontextmanager
from typing import Dict, List

import httpx
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from auth.authenticate import authenticate
from config import get_settings
from database.database import get_session
from routes.tools import check_user_exists
from services import PredictionService, UserService

settings = get_settings()
prediction_services: Dict[str, PredictionService] = {}


@asynccontextmanager
async def lifespan(app: APIRouter):
    prediction_services['main'] = PredictionService()
    yield
    prediction_services.clear()


predict_route = APIRouter(tags=["predict"], lifespan=lifespan)


@predict_route.post("/task/create")
async def create_task(
        file: UploadFile = File(...),
        user: dict = Depends(authenticate),
        session: Session = Depends(get_session)
) -> Dict[str, str]:
    user_db = UserService.get_user_by_id(user["id"], session)

    if user_db is None or user_db.login != user["login"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    if user_db.balance < settings.PREDICTION_COST:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough money")

    image_byte = await file.read()

    task_id = await prediction_services['main'].send_task(image_byte, user_db, session)
    return {"task_id": task_id}


@predict_route.post("/tasks/{task_id}/completion")
async def notify_task_completion(task_id: str, session: Session = Depends(get_session)):
    """
    Обрабатывает уведомление о завершении задачи Celery.
    """
    prediction_db = prediction_services['main'].get_prediction_database_by_task_id(task_id, session)
    if prediction_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task does not exist")

    prediction_services['main'].save_task_result_to_database(prediction_db, session)

    return {"message": "Task completion received", "task_id": task_id}


def send_callback(task_id: str, callback_url: str):
    with httpx.Client() as client:
        response = client.post(callback_url,
                               data={"task_id": task_id}
                               )

        if response.status_code == 200:
            return response.json()["task_id"]
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")


@predict_route.get("/task/{id}/result", response_model=List[dict])
async def get_task_result(
        id: str,
        user: dict = Depends(authenticate),
        session: Session = Depends(get_session)):
    user_db = UserService.get_user_by_id(user["id"], session)
    check_user_exists(user_db, user)

    prediction_db = prediction_services['main'].get_prediction_database_by_task_id(id, session)

    return [
        {
            "lat": tree.lat,
            "lon": tree.lon
        }
        for tree in prediction_db.trees
    ]


@predict_route.get("/history", response_model=List[dict])
async def get_history(
        user: dict = Depends(authenticate),
        session: Session = Depends(get_session)
):
    # TODO: Права админа
    history = prediction_services['main'].get_prediction_history(session)
    return [
        {
            "id": pred.id,
            "user_id": pred.user_id,
            "input_data": pred.input_data,
            "prediction": pred.prediction,
            "created_at": pred.created_at.isoformat(),  # Преобразуем datetime
        }
        for pred in history
    ]


@predict_route.get("/history/user", response_model=List[dict])
async def get_prediction_history_by_user(
        user: dict = Depends(authenticate),
        session: Session = Depends(get_session)
):
    user_db = UserService.get_user_by_id(user["id"], session)
    check_user_exists(user_db, user)

    history, images = await PredictionService.get_prediction_history_by_user(user_db, session)
    return [
        {
            "prediction": pred.prediction,
            "cost": pred.cost,
            "created_at": pred.created_at.isoformat(),  # Преобразуем datetime
            "image": base64.b64encode(image).decode("utf-8")
        }
        for pred, image in zip(history, images)
    ]
