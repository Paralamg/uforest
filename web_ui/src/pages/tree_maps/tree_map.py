import json
import streamlit as st
import rasterio

from .components.map import render_tree_map
from .components.form import render_edit_form
from .utils.geotiff_loader import load_geotiff_bounds_and_url


def show_tree_map():
    # st.set_page_config(layout="wide")
    st.title("🌳 Интерактивная карта деревьев")
    st.caption("Загрузите GeoTIFF-файл и выберите дерево для редактирования его характеристик.")

    # Загрузка GeoTIFF карты
    tiff_file = st.file_uploader("Загрузите GeoTIFF-файл", type=["tif", "tiff"])
    tiff_layer = None
    if tiff_file:
        bounds, url = load_geotiff_bounds_and_url(tiff_file)
        if bounds and url:
            st.success("Файл загружен. Отображение на карте доступно.")
            tiff_layer = {"bounds": bounds, "url": url}
        else:
            st.error("Не удалось обработать GeoTIFF. Проверьте файл.")

    # Загрузка данных деревьев
    DATA_FILE = ".data/trees.json"
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            trees = json.load(f)
    except FileNotFoundError:
        trees = []

    # Отображение карты и выбор дерева
    selected_tree_id = render_tree_map(trees, tiff_layer)

    # Форма редактирования дерева
    if selected_tree_id:
        updated_tree = render_edit_form(trees, selected_tree_id)
        if updated_tree:
            for i, t in enumerate(trees):
                if t["id"] == updated_tree["id"]:
                    trees[i] = updated_tree
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(trees, f, ensure_ascii=False, indent=2)
            st.success("Данные дерева обновлены!")