import pika
from datetime import datetime

from config import RabbitMQConfig
from models import User, WelcomeMessage


class MessageProducer:
    """
    Pure RabbitMQ publisher.
    Has no knowledge of Celery or which tasks will consume the message.
    Publishes raw JSON to the queue and its job is done.
    """

    def __init__(self):
        self.connection = pika.BlockingConnection(RabbitMQConfig.get_connection_params())
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=RabbitMQConfig.QUEUE_NAME, durable=True)
        print(f"✓ Producer connected to RabbitMQ at {RabbitMQConfig.HOST}:{RabbitMQConfig.PORT}")

    def send_welcome_message(self, user: User) -> bool:
        """
        Build a welcome message and publish it as raw JSON to RabbitMQ.
        Does NOT know about Celery tasks — worker decides what to do.
        """
        try:
            message = WelcomeMessage(
                message_type='user.welcome',
                user=user,
                timestamp=datetime.now().isoformat()
            )

            self.channel.basic_publish(
                exchange='',
                routing_key=RabbitMQConfig.QUEUE_NAME,
                body=message.to_json(),
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                    content_type='application/json',
                )
            )

            print(f"✓ Message published for: {user.name} (ID: {user.user_id})")
            return True

        except Exception as e:
            print(f"✗ Failed to publish message: {e}")
            return False

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("✓ Producer connection closed")


def main():
    """Example usage of MessageProducer."""
    producer = MessageProducer()

    users = [
        User(
            user_id="USR001",
            name="John Doe",
            email="john.doe@example.com",
            mobile="+1-555-0101"
        ),
        User(
            user_id="USR002",
            name="Jane Smith",
            email="jane.smith@example.com",
            mobile="+1-555-0102"
        ),
        User(
            user_id="USR003",
            name="Bob Johnson",
            email="bob.johnson@example.com",
            mobile="+1-555-0103"
        )
    ]

    try:
        for user in users:
            producer.send_welcome_message(user)
    finally:
        producer.close()


if __name__ == '__main__':
    main()
