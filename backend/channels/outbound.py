"""
Outbound message senders - one function per channel.
Each sender knows how to deliver a message through its platform API.
"""
import logging
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from twilio.rest import Client as TwilioClient

from backend.config import settings
from backend.models.agent import Agent
from backend.models.conversation import ChannelType
from backend.models.meta_connection import AgentMetaConnection

logger = logging.getLogger(__name__)


async def send_reply(
    db: AsyncSession,
    agent: Agent,
    channel: ChannelType,
    recipient_id: str,
    message: str,
):
    """Route outbound message to the correct channel sender."""
    senders = {
        ChannelType.SMS: _send_sms,
        ChannelType.FACEBOOK: _send_facebook,
        ChannelType.INSTAGRAM: _send_instagram,
        ChannelType.EMAIL: _send_email,
        ChannelType.LEAD_FORM: _send_noop,  # lead forms don't get real-time replies
        ChannelType.WEB_CHAT: _send_noop,   # handled via WebSocket separately
    }
    sender = senders.get(channel, _send_noop)
    try:
        await sender(db, agent, recipient_id, message)
    except Exception:
        logger.exception(f"Failed to send {channel.value} reply to {recipient_id}")


async def _get_meta_access_token(db: AsyncSession, agent: Agent) -> str:
    result = await db.execute(
        select(AgentMetaConnection).where(AgentMetaConnection.agent_id == agent.id)
    )
    connection = result.scalar_one_or_none()
    if connection and connection.page_access_token:
        return connection.page_access_token
    return settings.meta_page_access_token


async def _send_sms(db: AsyncSession, agent: Agent, recipient: str, message: str):
    """Send SMS via Twilio."""
    if not settings.twilio_account_sid:
        logger.warning("Twilio not configured, skipping SMS send")
        return

    client = TwilioClient(settings.twilio_account_sid, settings.twilio_auth_token)
    # Twilio's Python SDK is synchronous, so we call it directly
    # In production, this should be offloaded to a Celery task
    from_number = agent.twilio_phone_number or settings.twilio_phone_number
    client.messages.create(
        body=message,
        from_=from_number,
        to=recipient,
    )
    logger.info(f"SMS sent to {recipient}")


async def _send_facebook(db: AsyncSession, agent: Agent, recipient: str, message: str):
    """Send message via Facebook Messenger Graph API."""
    token = await _get_meta_access_token(db, agent)
    if not token:
        logger.warning("Meta page access token not configured")
        return

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://graph.facebook.com/v19.0/me/messages",
            params={"access_token": token},
            json={
                "recipient": {"id": recipient},
                "message": {"text": message},
            },
        )
        if resp.status_code != 200:
            logger.error(f"Facebook send failed: {resp.text}")


async def _send_instagram(db: AsyncSession, agent: Agent, recipient: str, message: str):
    """Send message via Instagram Messaging API (same Graph API, different endpoint)."""
    token = await _get_meta_access_token(db, agent)
    if not token:
        logger.warning("Meta page access token not configured")
        return

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://graph.facebook.com/v19.0/me/messages",
            params={"access_token": token},
            json={
                "recipient": {"id": recipient},
                "message": {"text": message},
            },
        )
        if resp.status_code != 200:
            logger.error(f"Instagram send failed: {resp.text}")


async def _send_email(db: AsyncSession, agent: Agent, recipient: str, message: str):
    """Send email reply via SendGrid."""
    if not settings.sendgrid_api_key:
        logger.warning("SendGrid not configured, skipping email send")
        return

    from_email = agent.email_inbox or settings.sendgrid_from_email

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {settings.sendgrid_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "personalizations": [{"to": [{"email": recipient}]}],
                "from": {"email": from_email},
                "subject": f"Re: Your inquiry with {agent.business_name}",
                "content": [{"type": "text/plain", "value": message}],
            },
        )
        if resp.status_code not in (200, 202):
            logger.error(f"SendGrid send failed: {resp.text}")


async def _send_noop(db: AsyncSession, agent: Agent, recipient: str, message: str):
    """No-op sender for channels that don't support push replies."""
    logger.debug(f"Noop send for recipient={recipient}")
