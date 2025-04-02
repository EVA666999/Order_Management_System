from celery import Celery
from app.core.config import settings

celery_app = Celery('orders', 
                    broker=settings.CELERY_BROKER_URL,
                    backend=settings.CELERY_RESULT_BACKEND)

@celery_app.task
def process_order(order_data):
    print(f"Processing order: {order_data}")