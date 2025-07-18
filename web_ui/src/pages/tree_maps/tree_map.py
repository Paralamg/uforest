import streamlit as st
import folium
from folium.plugins import MarkerCluster
import pandas as pd
import numpy as np
from streamlit_folium import st_folium
from datetime import datetime

# Глобальная настройка
CIRCLE_RADIUS = 6

MAP_TILES = {
    "Тёмная (CartoDB Dark Matter)": "CartoDB dark_matter",
    "Светлая (CartoDB Positron)": "CartoDB positron",
}

@st.cache_data
def load_data(n_points=500):
    np.random.seed(42)
    today = pd.Timestamp.today()

    # Генерация случайной даты посадки за последние 100 лет
    planting_start = today - pd.DateOffset(years=100)
    planting_dates = pd.to_datetime(
        np.random.randint(planting_start.value // 10**9, today.value // 10**9, n_points), unit='s'
    )

    # Генерация случайной даты последнего обслуживания (в пределах 3 лет)
    maintenance_start = today - pd.DateOffset(years=3)
    last_maintenance_dates = pd.to_datetime(
        np.random.randint(maintenance_start.value // 10**9, today.value // 10**9, n_points), unit='s'
    )

    data = {
        'lat': np.random.uniform(55.5, 56.5, n_points),
        'lon': np.random.uniform(37.3, 38.0, n_points),
        'type': np.random.choice(['Дуб', 'Сосна', 'Берёза', 'Клён'], n_points),
        'planting_date': planting_dates,
        'last_maintenance': last_maintenance_dates,
        'crown_area': np.random.uniform(1, 50, n_points),
    }

    df = pd.DataFrame(data)
    df['id'] = df.index + 1  # ID начинаются с 1

    today = pd.Timestamp.today()

    # Вычисление возраста и дней с последнего обслуживания
    df['age'] = df['planting_date'].apply(
        lambda d: today.year - d.year - ((today.month, today.day) < (d.month, d.day))
    )
    df['days_since_maintenance'] = (today - df['last_maintenance']).dt.days

    return df

def get_color_by_days(days):
    if days < 365:
        return 'green'
    elif days < 730:
        return 'yellow'
    else:
        return 'red'

def create_map(filtered_df):
    m = folium.Map(location=[55.7522, 37.6156], zoom_start=10, control_scale=True)

    for name, tile in MAP_TILES.items():
        folium.TileLayer(tile, name=name).add_to(m)

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
    st.markdown("### Фильтры и настройки")

    df = load_data()

    with st.sidebar:
        st.header("Параметры фильтрации")

        selected_types = st.multiselect(
            'Типы деревьев',
            options=df['type'].unique(),
            default=list(df['type'].unique())
        )

        age_min, age_max = int(df['age'].min()), int(df['age'].max())
        age_range = st.slider(
            'Возраст (лет)',
            min_value=age_min,
            max_value=age_max,
            value=(age_min, age_max)
        )

        crown_min, crown_max = float(df['crown_area'].min()), float(df['crown_area'].max())
        crown_size = st.slider(
            'Площадь кроны (м²)',
            min_value=crown_min,
            max_value=crown_max,
            value=(crown_min, crown_max)
        )

        days_min, days_max = int(df['days_since_maintenance'].min()), int(df['days_since_maintenance'].max())
        days_range = st.slider(
            'Дней с последнего обслуживания',
            min_value=days_min,
            max_value=days_max,
            value=(days_min, days_max)
        )

    filtered_df = df[
        (df['type'].isin(selected_types)) &
        (df['age'].between(*age_range)) &
        (df['crown_area'].between(*crown_size)) &
        (df['days_since_maintenance'].between(*days_range))
    ]

    st.metric("Всего деревьев на карте", filtered_df.shape[0])

    st.subheader("🗺️ Карта распределения деревьев")

    map_obj = create_map(filtered_df)
    st_folium(map_obj, height=800, width=1200)

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

# Для запуска:
# show_tree_map()