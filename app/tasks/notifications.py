
import logging

from app.worker import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="notifications.send_task_created",
    autoretry_for=(TimeoutError, ConnectionError),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    max_retries=5,
)
def send_task_created_notification(
    self,
    task_id: int,
    recipient_email: str,
) -> dict:
    logger.info(
        "Processing task notification",
        extra={"task_id": task_id},
    )

    # Replace this with a real email-provider call.
    # This placeholder does not send an email.
    logger.info(
        "Notification placeholder executed",
        extra={"task_id": task_id},
    )

    return {
        "task_id": task_id,
        "status": "processed",
    }
    
