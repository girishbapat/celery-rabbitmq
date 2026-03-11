"""
Celery Consumer Bridge
----------------------
Listens to the raw RabbitMQ queue (via pika) and dispatches every message
to the `welcome.route_message` Celery task.

The producer publishes plain JSON.
This bridge decides to hand it to Celery.
Celery tasks decide what to do with it.

Producer has ZERO knowledge of tasks.
"""

import json
import pika

from config import RabbitMQConfig
from celery_tasks import route_message


class CeleryConsumerBridge:
    """
    Reads raw JSON messages from RabbitMQ and dispatches them to
    the Celery router task. Adding a new task never requires changes here
    or in producer.py — only in celery_tasks.py.
    """

    def __init__(self):
        self.connection = pika.BlockingConnection(RabbitMQConfig.get_connection_params())
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=RabbitMQConfig.QUEUE_NAME, durable=True)
        self.channel.basic_qos(prefetch_count=1)
        print(f"✓ Consumer bridge connected to RabbitMQ at {RabbitMQConfig.HOST}:{RabbitMQConfig.PORT}")

    def _on_message(self, ch, method, properties, body):
        """Called by pika for every raw message off the queue."""
        try:
            message_payload = json.loads(body.decode())
            print(f"\n→ Raw message received, dispatching to Celery router...")

            # Hand off to the Celery route_message task.
            # route_message fans it out to all registered tasks.
            # This is the ONLY place that knows about Celery.
            # Uses the dedicated Celery queue, not the raw-message queue.
            route_message.apply_async(
                args=[message_payload],
                queue=RabbitMQConfig.CELERY_QUEUE_NAME,
            )

            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"✓ Dispatched to Celery router | message_type={message_payload.get('message_type')}")

        except Exception as e:
            print(f"✗ Failed to dispatch message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start(self):
        """Start consuming from the queue."""
        print(f"\n🎧 Listening on queue '{RabbitMQConfig.QUEUE_NAME}'...")
        print("Press CTRL+C to stop.\n")
        self.channel.basic_consume(
            queue=RabbitMQConfig.QUEUE_NAME,
            on_message_callback=self._on_message,
            auto_ack=False,
        )
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("\n✓ Stopping consumer bridge...")
            self.channel.stop_consuming()
        finally:
            self.close()

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("✓ Consumer bridge connection closed")


def main():
    bridge = CeleryConsumerBridge()
    bridge.start()


if __name__ == '__main__':
    main()
