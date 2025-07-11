import streamlit as st
from PIL import Image


def show_home():
    st.title("Главная")
    st.write("Сайт предназначен преобразования изображения с формулой в Latex текст.")
    st.write("Стоимость одного предсказания 10 монет.")

    st.write("Пример: ")
    with st.chat_message("user"):
        st.image(Image.open("example/example.png"), caption="Загруженное изображение")
    result = r"\Delta\psi=\frac{\hat{O}^{^{2}}\Psi}{\hat{O}{\bf x}^{^{2}}}+\frac{\hat{O}^{^{2}}\Psi}{\hat{O}{\bf y}^{^{2}}}+\frac{\hat{O}^{^{2}}\Psi}{\hat{O}{\bf z}^{^{2}}}"
    with st.chat_message("assistant"):
        st.text("Результат предсказания:")
        st.write(result)
        st.text("Формула в формате Latex:")
        st.latex(result)


if __name__ == "__main__":
    show_home()
