"""
Celery worker configuration and background tasks.
"""
from celery import Celery
from backend.config import settings

celery_app = Celery(
    "conduit",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@celery_app.task(name="conduit.send_followup")
def send_followup(conversation_id: str, agent_id: str):
    """
    Background task: send a follow-up message if the lead goes quiet.
    Can be scheduled with countdown (e.g., 30 minutes after last message).
    """
    # This will be expanded to re-engage cold leads
    pass


@celery_app.task(name="conduit.sync_crm")
def sync_crm(lead_id: str, agent_id: str):
    """Background task: push lead to CRM without blocking the webhook response."""
    pass
