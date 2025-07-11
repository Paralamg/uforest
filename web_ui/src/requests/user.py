import httpx
import streamlit as st

from config import get_settings

settings = get_settings()


def sign_up(login: str, password: str) -> str:
    with httpx.Client() as client:
        response = client.post(
            f"{settings.APP_SERVICE_URL}/user/signup",
            json={"login": login, "password": password}
        )
        if response.status_code != 200:
            return response.json()["detail"]
        return response.json()["message"]


def sign_in(username: str, password: str) -> str | None:
    with httpx.Client() as client:
        response = client.post(
            f"{settings.APP_SERVICE_URL}/user/signin",
            data={"username": username, "password": password}
        )
        if response.status_code != 200:
            return response.json()["detail"]
        type_token = response.json()["token_type"]
        token = response.json()["access_token"]
        auth_token = {"Authorization": f"{type_token} {token}"}
        st.session_state.jwt = auth_token


def get_user_balance() -> int:
    with httpx.Client() as client:
        response = client.get(f"{settings.APP_SERVICE_URL}/user/balance",
                              headers=st.session_state.jwt)
        if response.status_code == 200:
            return response.json()["balance"]
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")
