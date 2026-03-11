# RabbitMQ and Celery Welcome Messages

A Python application that sends welcome messages as JSON and uses RabbitMQ as the broker for Celery workers. Two Celery tasks consume each message: one prints the full JSON payload and the other prints a greeting for the user.

## Project Structure

```
rabbitmq-test/
├── config.py          # RabbitMQ configuration
├── celery_app.py      # Celery application setup
├── celery_consumer.py # Bridge: raw RabbitMQ message -> Celery router task
├── celery_tasks.py    # Celery tasks consuming welcome messages
├── celery_worker.py   # Small runner to start a Celery worker
├── models.py          # User and WelcomeMessage data models
├── producer.py        # Pure publisher: sends raw JSON to RabbitMQ
├── requirements.txt   # Python dependencies
├── .env              # Environment variables
└── README.md         # This file
```

## Setup

### Prerequisites
- Python 3.7+
- RabbitMQ server running (locally or remotely)

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure RabbitMQ connection (optional):**
   
   Edit `.env` file to set your RabbitMQ credentials:
   ```
   RABBITMQ_HOST=localhost
   RABBITMQ_PORT=5672
   RABBITMQ_USER=guest
   RABBITMQ_PASSWORD=guest
   QUEUE_NAME=welcome_messages
   ```

### Running with Docker (Optional)

If you don't have RabbitMQ installed, you can run it using Docker:

```bash
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3-management
```

This will:
- Start RabbitMQ on port 5672
- Enable the management UI on port 15672 (username: guest, password: guest)

## Usage

### 1. Start the Celery Worker

In one terminal, start the Celery worker that consumes messages from RabbitMQ:

```bash
python celery_worker.py
```

You should see the worker connect to RabbitMQ and register the two tasks.

### 2. Start the Consumer Bridge

In another terminal, start the bridge that consumes raw RabbitMQ messages and routes them to Celery:

```bash
python celery_consumer.py
```

### 3. Send Welcome Messages

In another terminal, run the producer to publish JSON messages:

```bash
python producer.py
```

The producer publishes raw messages:
```
✓ Message published for: John Doe (ID: USR001)
✓ Message published for: Jane Smith (ID: USR002)
✓ Message published for: Bob Johnson (ID: USR003)
```

### 4. View Worker Output

The Celery worker will process both tasks for each message:
```
📦 RAW WELCOME MESSAGE
{
  "message_type": "user.welcome",
  "user": {
    "user_id": "USR001",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "mobile": "+1-555-0101"
  },
  "timestamp": "2026-03-11T10:30:45.123456"
}
✓ Raw message printed for John Doe

👋 Hello John Doe! Welcome aboard. Your registered email is john.doe@example.com.
```

## Message Format

Messages are sent as JSON in the following format:

```json
{
  "message_type": "user.welcome",
  "user": {
    "user_id": "USR001",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "mobile": "+1-555-0101"
  },
  "timestamp": "2026-03-11T10:30:45.123456"
}
```

## Celery Tasks

The two Celery tasks live in `celery_tasks.py`:

- `print_raw_message` prints the complete JSON payload.
- `greet_user` prints a friendly greeting using the user's name.

To add custom actions, extend those tasks. For example:

- Send welcome emails
- Update user database
- Trigger additional workflows
- Log to external services

```python
@celery_app.task
def greet_user(message_payload: dict):
  message = WelcomeMessage.from_dict(message_payload)
  user = message.user
  # send_email(user.email, "Welcome!")
  # db.save_welcome_log(user.user_id)
```

## Features

- ✅ JSON message format for structured data
- ✅ Producer is decoupled from Celery task names
- ✅ RabbitMQ broker integration with Celery
- ✅ Consumer bridge routes raw messages to Celery dynamically
- ✅ Two independent Celery tasks run for each welcome message
- ✅ Easy worker startup via `python celery_worker.py`
- ✅ Configurable via `.env` file

## Troubleshooting

**Connection refused error:**
- Make sure RabbitMQ is running on the configured host and port
- Check your `.env` configuration

**Messages not being consumed:**
- Ensure `python celery_worker.py` is running before sending messages
- Check that both producer and worker use the same RabbitMQ credentials

**Permission denied:**
- Verify RabbitMQ username and password in `.env`
- Default credentials are `guest:guest`
