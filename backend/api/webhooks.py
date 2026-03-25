"""
Webhook endpoints - the entry point for all inbound messages from external channels.
Each channel (Twilio, Meta, SendGrid, lead forms) posts here.
"""
import hashlib
import hmac
import logging
from fastapi import APIRouter, Request, HTTPException, Depends, Form, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.database import get_db
from backend.models.agent import Agent
from backend.models.conversation import ChannelType
from backend.channels.router import route_inbound_message

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


# ── Twilio SMS Webhook ──

@router.post("/sms")
async def twilio_sms_webhook(
    request: Request,
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(""),
    MessageSid: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    """Twilio sends POST form data when an SMS arrives."""
    # Find the agent that owns this phone number
    result = await db.execute(
        select(Agent).where(Agent.twilio_phone_number == To, Agent.is_active == True)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        logger.warning(f"SMS to unregistered number: {To}")
        return {"status": "ignored"}

    await route_inbound_message(
        db=db,
        agent=agent,
        channel=ChannelType.SMS,
        sender_id=From,
        message_text=Body,
        channel_message_id=MessageSid,
    )
    # Twilio expects a TwiML response, but empty 200 is fine for async processing
    return ""


# ── Meta (Facebook Messenger + Instagram) Webhook ──

@router.get("/meta")
async def meta_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """Meta webhook verification handshake."""
    if hub_mode == "subscribe" and hub_verify_token == settings.meta_verify_token:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/meta")
async def meta_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Meta sends JSON payloads for Messenger and Instagram messages.
    We verify the signature, parse the event, and route to the right agent.
    """
    body = await request.body()

    # Verify signature
    signature = request.headers.get("X-Hub-Signature-256", "")
    if settings.meta_app_secret:
        expected = "sha256=" + hmac.new(
            settings.meta_app_secret.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(status_code=403, detail="Invalid signature")

    data = await request.json()

    for entry in data.get("entry", []):
        page_id = entry.get("id", "")

        # Messenger messages
        for messaging_event in entry.get("messaging", []):
            sender_id = messaging_event.get("sender", {}).get("id", "")
            message = messaging_event.get("message", {})
            text = message.get("text", "")
            message_id = message.get("mid", "")

            if not text:
                continue

            # Find agent by page ID
            result = await db.execute(
                select(Agent).where(Agent.meta_page_id == page_id, Agent.is_active == True)
            )
            agent = result.scalar_one_or_none()
            if agent:
                await route_inbound_message(
                    db=db,
                    agent=agent,
                    channel=ChannelType.FACEBOOK,
                    sender_id=sender_id,
                    message_text=text,
                    channel_message_id=message_id,
                )

        # Instagram messages (same structure under "messaging" for IG-connected pages)
        # Instagram uses the IG-scoped user ID as sender
        for messaging_event in entry.get("messaging", []):
            # Check if this is an IG message by looking at recipient matching IG account
            recipient_id = messaging_event.get("recipient", {}).get("id", "")
            result = await db.execute(
                select(Agent).where(Agent.meta_ig_account_id == recipient_id, Agent.is_active == True)
            )
            ig_agent = result.scalar_one_or_none()
            if ig_agent:
                sender_id = messaging_event.get("sender", {}).get("id", "")
                message = messaging_event.get("message", {})
                text = message.get("text", "")
                if text:
                    await route_inbound_message(
                        db=db,
                        agent=ig_agent,
                        channel=ChannelType.INSTAGRAM,
                        sender_id=sender_id,
                        message_text=text,
                        channel_message_id=message.get("mid", ""),
                    )

    return {"status": "ok"}


# ── SendGrid Inbound Parse Webhook ──

@router.post("/email")
async def email_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """SendGrid Inbound Parse sends form data with email content."""
    form = await request.form()
    to_email = form.get("to", "")
    from_email = form.get("from", "")
    subject = form.get("subject", "")
    text_body = form.get("text", "")

    # Extract the actual email address from "Name <email>" format
    import re
    email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", to_email)
    clean_to = email_match.group() if email_match else to_email

    result = await db.execute(
        select(Agent).where(Agent.email_inbox == clean_to, Agent.is_active == True)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        logger.warning(f"Email to unregistered inbox: {clean_to}")
        return {"status": "ignored"}

    # Combine subject and body for the AI
    full_message = f"Subject: {subject}\n\n{text_body}" if subject else text_body

    await route_inbound_message(
        db=db,
        agent=agent,
        channel=ChannelType.EMAIL,
        sender_id=from_email,
        message_text=full_message,
        channel_message_id="",
    )
    return {"status": "ok"}


# ── Lead Form Webhook ──

@router.post("/lead-form/{agent_id}")
async def lead_form_webhook(
    agent_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Generic lead form webhook. Accepts JSON with contact info.
    Can be embedded on any website or connected to form builders.
    """
    import uuid as uuid_mod
    try:
        aid = uuid_mod.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent ID")

    result = await db.execute(
        select(Agent).where(Agent.id == aid, Agent.is_active == True)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    data = await request.json()
    name = data.get("name", "")
    phone = data.get("phone", "")
    email = data.get("email", "")
    message = data.get("message", "")
    service = data.get("service", "")
    address = data.get("address", "")

    # Build a natural language message from the form data
    intro_parts = []
    if name:
        intro_parts.append(f"My name is {name}.")
    if service:
        intro_parts.append(f"I'm interested in {service}.")
    if address:
        intro_parts.append(f"My address is {address}.")
    if message:
        intro_parts.append(message)

    sender_id = email or phone or "form-lead"

    await route_inbound_message(
        db=db,
        agent=agent,
        channel=ChannelType.LEAD_FORM,
        sender_id=sender_id,
        message_text=" ".join(intro_parts) or "I'd like to learn more about your services.",
        channel_message_id="",
        initial_lead_data={
            "name": name,
            "phone": phone,
            "email": email,
            "address": address,
            "service_requested": service,
        },
    )
    return {"status": "received", "message": "Thank you! We'll be in touch shortly."}
