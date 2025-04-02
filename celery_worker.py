from app.tasks.order_task import celery_app

if __name__ == '__main__':
    celery_app.start()