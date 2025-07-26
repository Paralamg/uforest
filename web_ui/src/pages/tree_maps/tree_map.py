import streamlit as st
import folium
import pandas as pd
import numpy as np
import tempfile
import rasterio
import time

from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from datetime import datetime
from rasterio.plot import reshape_as_image
from rasterio.warp import transform_bounds
from PIL import Image
from typing import List

from ...requests.prediction import create_task, get_task_result
from ...logger import get_logger

logging = get_logger()
# Константы
CIRCLE_RADIUS = 6
MAP_TILES = {
    "Тёмная (CartoDB Dark Matter)": "CartoDB dark_matter",
    "Светлая (CartoDB Positron)": "CartoDB positron",
}

class Result:
    image = None
    task_id: str | None = None
    prediction: pd.DataFrame = pd.DataFrame()
    image_path: str | None = None
    image_bounds = None



def predict(image, name):
    task_id = create_task(image, name)
    if task_id:
        while st.session_state.result.prediction.empty:
            time.sleep(1)
            print("Шаг")
            st.session_state.result.prediction = get_task_result(task_id)
        # st.rerun()

def get_color_by_days(days):
    if days < 365:
        return 'green'
    elif days < 730:
        return 'yellow'
    else:
        return 'red'

def process_geotiff(uploaded_file, max_width=1024):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tif") as tmp:
        tmp.write(uploaded_file)
        path = tmp.name

    with rasterio.open(path) as src:
        image = src.read()
        bounds = src.bounds
        src_crs = src.crs
        bounds_wgs84 = transform_bounds(src_crs, "EPSG:4326", *bounds)

        img = reshape_as_image(image)
        if img.shape[2] > 3:
            img = img[:, :, :3]

        img_pil = Image.fromarray(img)

        if img_pil.width > max_width:
            ratio = max_width / img_pil.width
            new_size = (int(img_pil.width * ratio), int(img_pil.height * ratio))
            img_pil = img_pil.resize(new_size)

        img_path = path + ".png"
        img_pil.save(img_path, optimize=True)

        min_lon, min_lat, max_lon, max_lat = bounds_wgs84
        bounds_latlon = [[min_lat, min_lon], [max_lat, max_lon]]

    return img_path, bounds_latlon

def create_map(filtered_df=None, image_path=None, image_bounds=None, show_trees=False, show_image=False):
    # Автоцентрирование по изображению или дефолтная точка
    
    if image_bounds:
        south, west = image_bounds[0]
        north, east = image_bounds[1]
        center_lat = (south + north) / 2
        center_lon = (west + east) / 2
        m = folium.Map(location=[center_lat, center_lon], zoom_start=15, control_scale=True)
    else:
        m = folium.Map(location=[55.7522, 37.6156], zoom_start=10, control_scale=True)

    for name, tile in MAP_TILES.items():
        folium.TileLayer(tile, name=name).add_to(m)

    if show_image and image_path and image_bounds:
        folium.raster_layers.ImageOverlay(
            image=image_path,
            bounds=image_bounds,
            opacity=0.6,
            name="GeoTIFF слой"
        ).add_to(m)

    if show_trees and filtered_df is not None:
        marker_cluster = MarkerCluster(name="Деревья").add_to(m)
        for _, row in filtered_df.iterrows():
            popup = folium.Popup(f"""
                <b>ID:</b> {row['id']}<br>
                <b>Тип:</b> {row['type']}<br>
                <b>Возраст:</b> {row['age']} лет<br>
                <b>Дней с последнего обслуживания:</b> {row['days_since_maintenance']}<br>
                <b>Последнее обслуживание:</b> {row['last_maintenance'].strftime('%d.%m.%Y')}<br>
                <b>Координаты:</b> {row['lat']:.5f}, {row['lon']:.5f}<br>
                <b>Дата посадки:</b> {row['planting_date'].strftime('%d.%m.%Y')}<br>
                <b>Площадь кроны:</b> {row['crown_area']:.1f} м²<br>
            """, max_width=300)

            color = get_color_by_days(row['days_since_maintenance'])

            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=CIRCLE_RADIUS,
                color=color,
                fill=True,
                fill_opacity=0.7,
                popup=popup
            ).add_to(marker_cluster)

    folium.LayerControl(position='topright').add_to(m)
    return m

def show_tree_map():
    st.title('🌳 Интерактивная карта деревьев')
    # Инициализация состояний
    if "uploaded_image" not in st.session_state:
        st.session_state.uploaded_image = None
    if "result" not in st.session_state:
        st.session_state.result = Result()

    upload_container = st.container()
    send_button_placeholder = st.empty()

    with upload_container:
        uploaded_file = st.file_uploader(
            "Загрузите PNG-изображение",
            type=["tif", "tiff"],
        )

        if uploaded_file is not None:
            st.session_state.uploaded_image = uploaded_file

    # Обработка отправки изображения
    if st.session_state.uploaded_image is not None:
        if send_button_placeholder.button("📤 Отправить", key="send_button"):
            send_button_placeholder.empty()  # Мгновенно скрываем кнопку
            image = st.session_state.uploaded_image
            st.session_state.uploaded_image = None
            st.session_state.result.prediction = pd.DataFrame()
            st.session_state.result.task_id = None
            name = image.name
            st.session_state.result.image = image.read()
            st.session_state.result.image_bounds = None
            st.session_state.result.image_path = None
            

            with st.spinner("Модель обрабатывает изображение...", show_time=True):
                predict(st.session_state.result.image, name)
                st.session_state.result.image_path, st.session_state.result.image_bounds = process_geotiff(st.session_state.result.image)
                logging.info(f"image_path {st.session_state.result.prediction}")  


    show_image = st.checkbox('Показать исходное изображение', value=False) and st.session_state.result.image_path is not None

    if st.session_state.result.prediction.empty:
        show_trees = False
    else:
        show_trees = True

    if show_trees and not st.session_state.result.prediction.empty:
        df = st.session_state.result.prediction
        with st.sidebar:
            st.header("Параметры фильтрации")
            selected_types = st.multiselect(
                'Типы деревьев',
                options=df['type'].unique(),
                default=list(df['type'].unique())
            )
            age_range = st.slider('Возраст (лет)', int(df['age'].min()), int(df['age'].max()), (int(df['age'].min()), int(df['age'].max())))
            crown_range = st.slider('Площадь кроны (м²)', float(df['crown_area'].min()), float(df['crown_area'].max()), (float(df['crown_area'].min()), float(df['crown_area'].max())))
            days_range = st.slider('Дней с последнего обслуживания', int(df['days_since_maintenance'].min()), int(df['days_since_maintenance'].max()), (int(df['days_since_maintenance'].min()), int(df['days_since_maintenance'].max())))

        filtered_df = df[
            (df['type'].isin(selected_types)) &
            (df['age'].between(*age_range)) &
            (df['crown_area'].between(*crown_range)) &
            (df['days_since_maintenance'].between(*days_range))
        ]
        st.metric("Всего деревьев на карте", filtered_df.shape[0])
    else:
        filtered_df = None

    st.subheader("🗺️ Карта")
    m = create_map(
        filtered_df=filtered_df,
        image_path=st.session_state.result.image_path,
        image_bounds=st.session_state.result.image_bounds,
        show_trees=show_trees,
        show_image=show_image
    )
    st_folium(m, height=800, width=1200)

    if show_trees:
        st.markdown("### 🟢 Легенда по обслуживанию")
        legend_items = {
            'Зелёный (<1 года)': 'green',
            'Жёлтый (1–2 года)': 'yellow',
            'Красный (>2 лет)': 'red'
        }
        cols = st.columns(len(legend_items))
        for i, (label, color) in enumerate(legend_items.items()):
            cols[i].markdown(f"""
            <div style="display: flex; align-items: center;">
                <div style="width: 20px; height: 20px; background-color: {color}; margin-right: 10px;"></div>
                {label}
            </div>
            """, unsafe_allow_html=True)

        if st.checkbox('Показать исходные данные'):
            st.dataframe(filtered_df)

# Запуск
if __name__ == "__main__":
    show_tree_map()