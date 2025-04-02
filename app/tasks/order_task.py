from celery import Celery
from app.core.config import settings
import time

celery  = Celery('orders', 
                    broker=settings.CELERY_BROKER_URL,
                    backend=settings.CELERY_RESULT_BACKEND)

@celery.task
def process_order(order_id):
    time.sleep(2)
    print(f"Order {order_id} processed")