import datetime

import streamlit as st

from ..requests.balance import get_transaction_history


def show_transaction_history():
    st.title("💳 История транзакций")

    # Декодируем JSON
    transactions = get_transaction_history()

    if not transactions:
        st.info("История транзакций пуста.")
        return

    for transaction in transactions:
        transaction_id = transaction["id"]
        amount = transaction["amount"]
        description = transaction["description"]
        transaction_type = "Пополнение" if transaction["type"] == 0 else "Снятие"
        created_at = datetime.datetime.fromisoformat(transaction["created_at"]).strftime("%d.%m.%Y %H:%M")

        # Отображаем транзакцию
        with st.container():
            st.markdown(
                f"""
                <div style="background: #1E1E1E; border-radius: 10px; padding: 1rem; margin: 1rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="color: #FFFFFF; font-size: 1rem;">🆔 <b>ID:</b> {transaction_id}</div>
                    <div style="color: {'#2ecc71' if transaction['type'] == 0 else '#e74c3c'}; font-size: 1.5rem; font-weight: bold;">💰 {amount if transaction['type'] == 0 else -amount}</div>
                    <div style="color: #CCCCCC; font-size: 0.9rem;">📖 {description}</div>
                    <div style="color: {'#2ecc71' if transaction['type'] == 0 else '#e74c3c'}; font-size: 1rem; font-weight: bold;">{transaction_type}</div>
                    <div style="color: #AAAAAA; font-size: 0.8rem;">🕒 {created_at}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
