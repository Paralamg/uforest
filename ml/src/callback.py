import requests

from config import get_settings

settings = get_settings()


def notify_task_completion(task_id: str):
    """Отправляет HTTP-запрос в app для уведомления о завершении задачи."""
    url = f"{settings.APP_SERVICE_URL}/predict/tasks/{task_id}/completion"
    try:
        response = requests.post(url, json={"task_id": task_id})
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка при отправке callback запроса: {e}")
