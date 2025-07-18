import time

import pyperclip
import streamlit as st
from PIL import Image

from ..requests.prediction import create_task, get_task_result

pyperclip.set_clipboard("xsel")


class Result:
    image = None,
    task_id: str | None = None,
    prediction: str | None = None


def predict(image):
    task_id = create_task(image.read(), image.name)
    if task_id:
        while st.session_state.result.prediction == None:
            time.sleep(1)
            st.session_state.result.prediction = get_task_result(task_id)
        st.rerun()


def show_latex_chat():
    st.title("Image to Latex преобразователь")
    st.caption("🤖 Загрузите изображение c формулой, и модель вернёт результат в виде Latex текста.")

    # Инициализация состояний
    if "uploaded_image" not in st.session_state:
        st.session_state.uploaded_image = None
    if "result" not in st.session_state:
        st.session_state.result = Result()

    def copy_to_clipboard(text):
        pyperclip.copy(text)
        st.toast("Текст скопирован!")

    upload_container = st.container()
    send_button_placeholder = st.empty()

    with upload_container:
        uploaded_file = st.file_uploader(
            "Загрузите PNG-изображение",
            type=["png"],
        )

        if uploaded_file is not None:
            st.session_state.uploaded_image = uploaded_file

    # Обработка отправки изображения
    if st.session_state.uploaded_image is not None:
        if send_button_placeholder.button("📤 Отправить", key="send_button"):
            send_button_placeholder.empty()  # Мгновенно скрываем кнопку
            image = st.session_state.uploaded_image
            st.session_state.uploaded_image = None
            st.session_state.result.prediction = None
            st.session_state.result.task_id = None
            st.session_state.result.image = image

            with st.spinner("Модель обрабатывает изображение...", show_time=True):
                prediction = predict(image)

    if st.session_state.result.image is not None and st.session_state.result.prediction is not None:
        with st.chat_message("user"):
            st.image(Image.open(st.session_state.result.image), caption="Загруженное изображение")

        with st.chat_message("assistant"):
            st.text("Результат предсказания:")
            st.write(st.session_state.result.prediction)
            st.text("Формула в формате Latex:")
            st.latex(st.session_state.result.prediction)

            # TODO: Код снизу не работает из docker
            # if st.button("📋 Копировать", key=f"copy"):
            #     copy_to_clipboard(st.session_state.result.prediction)
