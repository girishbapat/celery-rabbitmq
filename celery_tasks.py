import json

from celery import group

from celery_app import celery_app
from models import WelcomeMessage


# ---------------------------------------------------------------------------
# Individual task handlers
# The producer knows nothing about these. Add / remove tasks freely here
# without ever touching producer.py.
# ---------------------------------------------------------------------------

@celery_app.task(name='welcome.print_raw_message')
def print_raw_message(message_payload: dict) -> None:
    """Task 1 — print the full JSON payload as-is."""
    message = WelcomeMessage.from_dict(message_payload)
    print('\n📦 RAW WELCOME MESSAGE')
    print(json.dumps(message.to_dict(), indent=2))
    print(f"✓ Raw message printed for {message.user.name}\n")


@celery_app.task(name='welcome.greet_user')
def greet_user(message_payload: dict) -> None:
    """Task 2 — print a friendly greeting for the new user."""
    message = WelcomeMessage.from_dict(message_payload)
    print(
        f"👋 Hello {message.user.name}! "
        f"Welcome aboard. Your registered email is {message.user.email}."
    )


# ---------------------------------------------------------------------------
# Router — the single entry-point the worker calls for every raw message.
# Add a new task above, then register it here. Producer never changes.
# ---------------------------------------------------------------------------

REGISTERED_TASKS = [
    print_raw_message,
    greet_user,
    # add future tasks here ↓
]


@celery_app.task(name='welcome.route_message')
def route_message(message_payload: dict) -> None:
    """
    Entry-point task: receives the raw message from the queue and fans it
    out to every task registered in REGISTERED_TASKS.
    The producer only ever publishes to this one task name.
    """
    workflow = group(task.s(message_payload) for task in REGISTERED_TASKS)
    workflow.apply_async()