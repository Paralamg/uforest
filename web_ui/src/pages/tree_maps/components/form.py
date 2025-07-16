import streamlit as st
from datetime import datetime

def render_edit_form(trees, selected_id):
    tree = next((t for t in trees if t["id"] == selected_id), None)
    if not tree:
        return None

    with st.sidebar.form("edit_form"):
        species = st.text_input("Вид дерева", value=tree["species"])
        crown_area = st.number_input("Площадь кроны (м²)", value=tree["crown_area"], step=0.1)
        planted = st.date_input("Дата посадки", value=parse_date(tree["planted"]))
        last_service = st.date_input("Последнее обслуживание", value=parse_date(tree["last_service"]))
        submitted = st.form_submit_button("💾 Сохранить")

        if submitted:
            return {
                **tree,
                "species": species,
                "crown_area": crown_area,
                "planted": planted.strftime("%d-%m-%Y"),
                "last_service": last_service.strftime("%d-%m-%Y")
            }
    return None

def parse_date(date_str):
    return datetime.strptime(date_str, "%d-%m-%Y").date()