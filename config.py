import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class RabbitMQConfig:
    """RabbitMQ configuration"""
    HOST = os.getenv('RABBITMQ_HOST', 'localhost')
    PORT = int(os.getenv('RABBITMQ_PORT', 5672))
    USER = os.getenv('RABBITMQ_USER', 'guest')
    PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
    VHOST = os.getenv('RABBITMQ_VHOST', '/')
    QUEUE_NAME = os.getenv('QUEUE_NAME', 'welcome_messages')
    # Separate queue for Celery tasks (keeps raw pika messages isolated)
    CELERY_QUEUE_NAME = os.getenv('CELERY_QUEUE_NAME', 'welcome_tasks')
    
    @classmethod
    def get_connection_params(cls):
        """Get RabbitMQ connection parameters"""
        import pika
        return pika.ConnectionParameters(
            host=cls.HOST,
            port=cls.PORT,
            virtual_host=cls.VHOST,
            credentials=pika.PlainCredentials(cls.USER, cls.PASSWORD),
            connection_attempts=3,
            retry_delay=2
        )

    @classmethod
    def get_celery_broker_url(cls):
        """Build Celery broker URL for RabbitMQ."""
        username = quote_plus(cls.USER)
        password = quote_plus(cls.PASSWORD)
        vhost = cls.VHOST if cls.VHOST.startswith('/') else f'/{cls.VHOST}'
        return f'amqp://{username}:{password}@{cls.HOST}:{cls.PORT}{vhost}'
