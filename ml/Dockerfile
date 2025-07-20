# 1. Используем официальный PyTorch образ с поддержкой CUDA 12.1
FROM pytorch/pytorch:2.7.1-cuda12.8-cudnn9-runtime

# 2. Обновим pip и установим зависимости системы
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    gcc \
    g++ \
    python3-dev \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Установим pip последней версии и зависимости из requirements.txt
RUN pip install --upgrade pip
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# 4. Установка Detectron2 (важно делать после установки torch и torchvision)
RUN pip install 'git+https://github.com/facebookresearch/detectron2.git'

# 5. Копируем проект и делаем DVC pull
WORKDIR /ml
COPY . /ml

# Устанавливаем DVC и вытягиваем данные
RUN pip install dvc[s3]

RUN adduser --disabled-password --gecos '' celeryuser

USER celeryuser

CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info", "--pool=solo"]
#CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info", "--concurrency=2"]
