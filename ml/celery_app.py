from celery import Celery, Task
from celery.signals import worker_process_init

from config import get_settings
from src.callback import notify_task_completion
from src.model_loader import load_model
from src.tree_detector.inference import process_geotiff
from src.preprocess import load_bytes_from_minio

settings = get_settings()

celery = Celery('ml_service',
                backend=settings.CELERY_RESULT_BACKEND,
                broker=settings.CELERY_BROKER,
                )

celery.conf.update(
    broker_connection_retry_on_startup=True,
    worker_proc_alive_timeout=10,
    worker_cancel_long_running_tasks_on_connection_loss=True
)

model = None


def load_ml_model(**kwargs):
    global model
    model = load_model()
    print("ML модель загружена в воркер")


worker_process_init.connect(load_ml_model)


class MyTask(Task):
    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """Вызывается после завершения задачи Celery."""
        notify_task_completion(task_id)


@celery.task(base=MyTask)
def predict(image_name: str):
    global model
    if model is None:
        raise ValueError("Модель не загружена")

    # Загрузка GeoTIFF из MinIO
    geotiff_bytes = load_bytes_from_minio(image_name)
    
    # Обработка файла
    coords = process_geotiff(geotiff_bytes, model)
    return coords
