import time

import streamlit as st
import json
import httpx
from config import get_settings

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


def get_prediction_history() -> json:
    with httpx.Client() as client:
        response = client.get(f"{settings.APP_SERVICE_URL}/predict/history/user",
                              headers=st.session_state.jwt)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")
