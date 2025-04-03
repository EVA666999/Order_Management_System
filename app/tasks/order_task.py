from celery import Celery
from app.core.config import settings
import time

# Создаем объект Celery
celery_app = Celery(
    "orders", broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND
)

# Настройка логирования
celery_app.conf.task_track_started = True
celery_app.conf.task_send_sent_event = True


@celery_app.task
def process_order(order_id):
    time.sleep(2)
    print(f"Order {order_id} processed")
