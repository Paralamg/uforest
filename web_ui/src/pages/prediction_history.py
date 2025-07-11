import base64
import datetime
import io

import streamlit as st
from PIL import Image

from ..requests.prediction import get_prediction_history


def show_predictions_history():
    st.title("📜 История предсказаний")

    # Декодируем JSON-объект
    with st.spinner("Загружаем историю...", show_time=True):
        history = get_prediction_history()

    if not history:
        st.info("История предсказаний пуста.")
        return

    for item in history:
        # Извлекаем данные
        prediction = item["prediction"]
        cost = item["cost"]
        created_at = datetime.datetime.fromisoformat(item["created_at"]).strftime("%d.%m.%Y %H:%M")
        image_bytes = base64.b64decode(item["image"])  # Декодируем изображение из Base64
        image = Image.open(io.BytesIO(image_bytes))  # Загружаем изображение в PIL

        # Отображаем карточку предсказания
        with st.container():
            st.image(image, caption="Входные данные", use_container_width=True)
            st.markdown(f"**Предсказание:** {prediction}")
            st.latex(prediction, help="Результат предсказания в виде Latex отображения")
            st.markdown(f"**Стоимость:** {cost} 💰")
            st.markdown(f"**Дата:** {created_at}")
            st.markdown("---")  # Разделитель между элементами
