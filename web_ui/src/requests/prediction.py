import time

import numpy as np

import streamlit as st
import pandas as pd
import json
import httpx
from config import get_settings
from ..logger import get_logger

logging = get_logger()

settings = get_settings()


def create_task(image_bytes: bytes, filename: str) -> str | None:
    files = {"file": (filename, image_bytes, "image/tif")}
    with httpx.Client() as client:
        response = client.post(f"{settings.APP_SERVICE_URL}/predict/task/create",
                               headers=st.session_state.jwt,
                               files=files,
                               )

        if response.status_code == 200:
            return response.json()["task_id"]
        elif response.json()["detail"] == "Not enough money":
            st.error("Недостаточно средств!")
            return None
            # st.rerun()
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")


def get_task_result(task_id: str) -> str:
    with httpx.Client() as client:
        response = client.get(f"{settings.APP_SERVICE_URL}/predict/task/{task_id}/result",
                              headers=st.session_state.jwt)
        if response.status_code == 200:
            return response.json()["prediction"]
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")


def get_task_result(task_id: str):
    """
    Получает результаты задачи с бэкенда и преобразует в DataFrame
    с добавлением вычисляемых полей.
    """
    endpoint = f"{settings.APP_SERVICE_URL}/predict/task/{task_id}/result"
    headers = st.session_state.jwt
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(endpoint, headers=headers)
            response.raise_for_status()  # Проверка на ошибки HTTP
            
            data = response.json()
            
            # Если нет данных
            if not data:
                logging.info("Нет данных")    
                return pd.DataFrame()
            
            # Преобразуем в DataFrame
            df = pd.DataFrame(data)
            logging.info(f"Данные получены, количество деревьев {len(df.index)}")  

            # Конвертация дат в datetime
            df['planting_date'] = pd.to_datetime(df['planting_date'])
            df['last_maintenance'] = pd.to_datetime(df['last_maintenance'])
            
            # Добавляем вычисляемые поля
            today = pd.Timestamp.today()
            df['age'] = np.random.randint(2, 41, size=len(df))
            df['days_since_maintenance'] = (today - df['last_maintenance']).dt.days
            logging.info(df)
            
            return df

    except httpx.HTTPStatusError as e:
        st.error(f"Ошибка сервера: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        st.error(f"Ошибка подключения: {e}")
    except Exception as e:
        st.error(f"Неизвестная ошибка: {str(e)}")
    
    return pd.DataFrame()  # Возвращаем пустой DataFrame при ошибках


def get_prediction_history() -> json:
    with httpx.Client() as client:
        response = client.get(f"{settings.APP_SERVICE_URL}/predict/history/user",
                              headers=st.session_state.jwt)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")
