import re

import streamlit as st

from src.pages import *
from src.requests.balance import top_up_balance
from src.requests.user import sign_in, sign_up, get_user_balance


def main():
    if "page" not in st.session_state:
        st.session_state.page = "Главная"
    if "jwt" not in st.session_state:
        st.session_state.jwt = None
    if "balance" not in st.session_state:  # Добавляем баланс в session_state
        st.session_state.balance = 1

    pages = {
        "Главная": show_home,
        "Карта деревьев": show_tree_map,
        "История предсказаний": show_predictions_history,
        "История транзакций": show_transaction_history,
    }

    with st.sidebar:
        if not st.session_state.jwt:
            auth_form()

        else:

            st.session_state.page = st.selectbox("Выберите страницу", pages.keys())
            st.session_state.balance = get_user_balance()
            st.markdown(
                f"""
                                <div style="
                                    background: #131313;
                                    border-radius: 10px;
                                    padding: 1rem;
                                    margin: 1rem 0;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                                ">
                                    <div style="font-size: 0.9rem; color: #FFFFFF;">Баланс</div>
                                    <div style="
                                        font-size: 1.5rem;
                                        font-weight: 600;
                                        color: #2ecc71;
                                        margin-top: 0.5rem;
                                    ">💰{st.session_state.balance}</div>
                                </div>
                            """,
                unsafe_allow_html=True
            )
            amount = st.number_input("Введите сумму пополнения", min_value=1, step=1)
            if st.button("Top up!"):
                top_up_balance(int(amount))
            if st.button("Sign Out"):
                st.session_state.jwt = None
                st.session_state.page = "Главная"
                st.rerun()

    # Отображение текущей страницы
    pages[st.session_state.page]()


def auth_form():
    st.title("Введите логин и пароль")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        error = validate_credentials(username, password)
        if error:
            st.toast(error)
        else:
            result = sign_up(username, password)
            st.toast(result)

    if st.button("Sign In"):
        error = validate_credentials(username, password)
        if error:
            st.toast(error)

        if error is None:
            sign_in_error = sign_in(username, password)
            if sign_in_error:
                st.toast(sign_in_error)
            else:
                st.toast("Пользователь авторизован")
                st.rerun()


def validate_credentials(username: str, password: str):
    if not username or not password:
        return "Username and password cannot be empty."
    if len(username) < 3:
        return "Username must be at least 3 characters long."
    if len(password) < 6:
        return "Password must be at least 6 characters long."
    if not re.match("^[a-zA-Z0-9_]+$", username):
        return "Username can only contain letters, numbers, and underscores."
    return None


if __name__ == "__main__":
    main()
