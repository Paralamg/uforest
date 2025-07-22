import random
import datetime

from typing import Sequence

from celery import Celery
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import get_settings
from models.user import User, Prediction, Tree, TreeType
from .balance_service import BalanceService
from ..image_service import ImageService
from ..logger import get_logger


image_service = ImageService()
settings = get_settings()
logging = get_logger(logger_name=__name__)


class PredictionService:
    def __init__(self):
        self.app = Celery(
            'other_service',
            broker=settings.CELERY_BROKER,
            backend=settings.CELERY_RESULT_BACKEND)

    async def send_task(self, image: bytes, user: User, session: Session) -> str | None:
        image_name = await image_service.upload_image(image)
        task = self.app.send_task('celery_app.predict', args=(image_name,))
        if task:
            BalanceService.make_transaction(user, settings.PREDICTION_COST, "Prediction", session)

            prediction_db = Prediction(
                user_id=user.id,
                input_data=image_name,
                task_id=task.id,
                task_status="STARTED",
                cost=settings.PREDICTION_COST
            )
            session.add(prediction_db)
            session.commit()
            logging.info(f"Пользователь {user.login}: создал задачу {task.id}")
            return task.id
        logging.error(f"Ошибка: создание задачи {task.id}, пользователь {user.login} ")
        return None
        
    
    def create_tree(self, prediction: tuple, prediction_db: Prediction, session: Session):

        tree_type = random.choice(list(TreeType))
        planting_date = datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 365))
        last_maintenance = datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30))
        crown_area = random.uniform(1.0, 100.0)  # Площадь кроны в квадратных метрах

        tree = Tree(
            type=tree_type,
            planting_date=planting_date,
            last_maintenance=last_maintenance,
            lat=prediction[0],
            lon=prediction[1],
            crown_area=crown_area,
            prediction_id=prediction_db.id

        )
        session.add(tree)
        session.commit()
        session.refresh(tree)

        logging.info(f"Дерево {tree.id}: создано")
        

    def save_task_result_to_database(self, prediction_db: Prediction, session: Session) -> None:
        result = self.app.AsyncResult(prediction_db.task_id)
        predictions = result.get()
        for prediction in predictions:
            self.create_tree(prediction, prediction_db, session)
            
        prediction_db.task_status = "READY"
        logging.info(f"Задача {prediction_db.task_id}: сохранена в БД")
        session.commit()
    

    def get_task_result(self, task_id, session: Session) -> str | None:
        prediction_db = self.get_prediction_database_by_task_id(task_id, session)
        if prediction_db is None:
            return None

        if prediction_db.prediction is None:
            return prediction_db.task_status

        return prediction_db.prediction

    @staticmethod
    def get_prediction_database_by_task_id(task_id, session: Session) -> Prediction | None:
        prediction = session.query(Prediction).filter(Prediction.task_id == task_id).first()
        if prediction:
            return prediction
        return None

    @staticmethod
    def get_prediction_history(session: Session) -> Sequence[Prediction]:
        query = select(Prediction)
        result = session.execute(query)
        prediction = result.scalars().all()
        return prediction

    @staticmethod
    async def get_prediction_history_by_user(user: User, session: Session) -> tuple[Sequence[Prediction], list[bytes]]:
        query = select(Prediction).filter(user.id == Prediction.user_id)
        result = session.execute(query)
        predictions = result.scalars().all()
        images = []
        for prediction in predictions:
            file_name = prediction.input_data
            image = await image_service.download_image(file_name)
            images.append(image)
        logging.info(f"Пользователь {user.login}: сделал запрос на получение истории предсказаний")
        return predictions, images
