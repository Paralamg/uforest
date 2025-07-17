import streamlit as st
import folium
from folium.plugins import MarkerCluster
import pandas as pd
import numpy as np
from streamlit_folium import st_folium


@st.cache_data
def load_data(n_points=500):
    data = {
        'lat': np.random.uniform(55.5, 56.5, n_points),
        'lon': np.random.uniform(37.3, 38.0, n_points),
        'type': np.random.choice(['Дуб', 'Сосна', 'Берёза', 'Клён'], n_points),
        'age': np.random.randint(1, 100, n_points),
        'crown_area': np.random.uniform(1, 50, n_points)
    }
    return pd.DataFrame(data)

# Настройка цветовой схемы
TYPE_COLORS = {
    'Дуб': '#1f77b4',
    'Сосна': '#2ca02c',
    'Берёза': '#d62728',
    'Клён': '#9467bd'
}

# Создание карты
def create_map(filtered_df):
    m = folium.Map(location=[55.7522, 37.6156], zoom_start=10)
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in filtered_df.iterrows():
        popup = folium.Popup(f"""
            Тип: {row['type']}<br>
            Возраст: {row['age']} лет<br>
            Площадь кроны: {row['crown_area']:.1f} м²
        """, max_width=250)

        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=row['crown_area'] / 5,
            color=TYPE_COLORS[row['type']],
            fill=True,
            fill_opacity=0.7,
            popup=popup
        ).add_to(marker_cluster)

    return m

def show_tree_map():
    # Загрузка данных (пример генерации тестовых данных)

    # Интерфейс Streamlit
    st.title('🌳 Интерактивная карта деревьев')
    st.markdown("""
    ### Фильтры данных
    Используйте параметры ниже для фильтрации отображаемых деревьев
    """)

    # Загрузка данных
    df = load_data()

    # Фильтры в сайдбаре
    with st.sidebar:
        st.header("Параметры фильтрации")
        selected_types = st.multiselect(
            'Выберите типы деревьев',
            options=TYPE_COLORS.keys(),
            default=list(TYPE_COLORS.keys())
        )

        age_range = st.slider(
            'Диапазон возраста (лет)',
            min_value=int(df['age'].min()),
            max_value=int(df['age'].max()),
            value=(20, 80)
        )

        crown_size = st.slider(
            'Площадь кроны (м²)',
            min_value=float(df['crown_area'].min()),
            max_value=float(df['crown_area'].max()),
            value=(5.0, 30.0)
        )

    # Применение фильтров
    filtered_df = df[
        (df['type'].isin(selected_types)) &
        (df['age'].between(*age_range)) &
        (df['crown_area'].between(*crown_size))
        ]

    # Отображение статистики
    st.metric("Всего деревьев на карте", filtered_df.shape[0])

    # Создание и отображение карты
    st.subheader("Карта распределения деревьев")
    map_obj = create_map(filtered_df)
    st_folium(map_obj, width=1200, height=600)

    # Легенда
    st.markdown("### Легенда")
    cols = st.columns(len(TYPE_COLORS))
    for i, (tree_type, color) in enumerate(TYPE_COLORS.items()):
        cols[i].markdown(f"""
        <div style="display: flex; align-items: center;">
            <div style="width: 20px; height: 20px; background-color: {color}; margin-right: 10px;"></div>
            {tree_type}
        </div>
        """, unsafe_allow_html=True)

    # Показ сырых данных
    if st.checkbox('Показать исходные данные'):
        st.dataframe(filtered_df)
