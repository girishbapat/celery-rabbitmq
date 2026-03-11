from celery import Celery

from config import RabbitMQConfig


celery_app = Celery(
    'welcome_messages',
    broker=RabbitMQConfig.get_celery_broker_url(),
    include=['celery_tasks'],
)

celery_app.conf.update(
    task_default_queue=RabbitMQConfig.CELERY_QUEUE_NAME,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    enable_utc=True,
    timezone='UTC',
)