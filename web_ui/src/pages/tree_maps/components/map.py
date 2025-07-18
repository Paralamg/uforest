import folium
import streamlit as st
from streamlit_folium import st_folium
from ..utils.helpers import get_color_by_date

def render_tree_map(trees, tiff_layer=None):
    center = [55.75, 37.62]  # по умолчанию Москва
    m = folium.Map(location=center, zoom_start=15, control_scale=True)

    # Добавим GeoTIFF как слой (если загружен)
    if tiff_layer:
        folium.raster_layers.ImageOverlay(
            name="GeoTIFF",
            image=tiff_layer["url"],
            bounds=tiff_layer["bounds"],
            opacity=0.6,
            interactive=True,
            cross_origin=False
        ).add_to(m)

    for tree in trees:
        color = get_color_by_date(tree["last_service"])
        popup = f"""
        <b>ID:</b> {tree["id"]}<br>
        <b>Вид:</b> {tree["species"]}<br>
        <b>Крона:</b> {tree["crown_area"]} м²<br>
        <b>Посадка:</b> {tree["planted"]}<br>
        <b>Обслуживание:</b> {tree["last_service"]}
        """
        folium.CircleMarker(
            location=tree["coords"],
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=popup,
            tooltip=f"ID {tree['id']}"
        ).add_to(m)

    st_map = st_folium(m, width=900, height=600)

    # Выбор дерева для редактирования
    st.sidebar.header("Редактирование дерева")
    selected = st.sidebar.selectbox(
        "Выберите ID дерева:",
        [tree["id"] for tree in trees]
    )
    return selected