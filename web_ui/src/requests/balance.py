import json

import streamlit as st
import httpx
from config import get_settings

settings = get_settings()


def top_up_balance(amount: int):
    with httpx.Client() as client:
        response = client.post(f"{settings.APP_SERVICE_URL}/balance/top-up",
                               headers=st.session_state.jwt,
                               json={"amount": amount},
                               )

        if response.status_code == 200:
            st.rerun()
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")


def get_transaction_history() -> json:
    with httpx.Client() as client:
        response = client.get(f"{settings.APP_SERVICE_URL}/balance/history/user",
                              headers=st.session_state.jwt)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")
