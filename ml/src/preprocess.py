from io import BytesIO

import requests
from PIL import Image
from minio import Minio

from config import get_settings

settings = get_settings()
minio_client = Minio(
    settings.MINIO_URL,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=True
)


def prepare_image(image: Image, engine):
    if not image.mode == "RGB":
        image = image.convert('RGB')

    pixel_values = engine(image, return_tensors="pt").pixel_values
    return pixel_values


def load_image_from_url(url) -> Image:
    response = requests.get(url)

    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        return image
    else:
        print("Ошибка загрузки изображения")


def load_bytes_from_minio(file_name: str) -> bytes:
    with minio_client.get_object(settings.MINIO_BUCKET_NAME, file_name) as response:
        return response.read()
