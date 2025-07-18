import asyncio
import io
import uuid

from PIL import Image
from minio import Minio

from config import get_settings


class ImageService:

    def __init__(self):
        settings = get_settings()
        self.minio_client = Minio(
            settings.MINIO_URL,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=True
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self.folder_name = settings.MINIO_FOLDER

    async def upload_image(self, image: bytes) -> str:
        unique_name = f"{self.folder_name}/{uuid.uuid4()}.tif"  # Сохраняем в "папку"
        image_stream = io.BytesIO(image)

        await asyncio.to_thread(
            self.minio_client.put_object,
            self.bucket_name,
            unique_name,
            data=image_stream,
            length=len(image),
            content_type="image/tif",
        )
        return unique_name

    async def download_image(self, filename: str) -> bytes:
        """Скачивает изображение из MinIO и возвращает его в виде байтов."""

        response = await asyncio.to_thread(
            self.minio_client.get_object,
            self.bucket_name,
            filename
        )
        image_bytes = response.read()
        return image_bytes


if __name__ == "__main__":
    service = ImageService()
    with Image.open(r'/Users/dmitryklimov/Downloads/68762df522caa22a41b139a5.tif') as img:
        img = img.convert("RGB")
        byte_io = io.BytesIO()
        img.save(byte_io, format="TIFF")
        value = byte_io.getvalue()
    file_name = asyncio.run(service.upload_image(value))
    print(file_name)
    image_bytes = asyncio.run(service.download_image(file_name))
    image_stream = io.BytesIO(image_bytes)
    image = Image.open(image_stream)
    image.show()
