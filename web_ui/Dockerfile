FROM python:3.11

# Установите GDAL и другие зависимости
RUN apt-get update && apt-get install -y \
    xclip \
    xsel \
    gdal-bin \
    libgdal-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Установите рабочую директорию
WORKDIR /web_ui

# Скопируйте файл зависимостей
COPY requirements.txt /web_ui/

# Установите переменную окружения для версии GDAL (при необходимости)
ENV GDAL_VERSION=3.6.2

# Обновите pip и установите зависимости
RUN pip install --upgrade pip && pip install -r /web_ui/requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

