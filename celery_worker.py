import os
from celery_app import celery_app


def main() -> None:
    # Use a unique hostname so multiple local workers never clash.
    hostname = os.getenv('CELERY_WORKER_NAME', 'welcome-worker@%h')
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--pool=solo',
        f'--hostname={hostname}',
    ])


if __name__ == '__main__':
    main()