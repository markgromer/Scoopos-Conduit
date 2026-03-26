"""
Channel router - the central hub that receives inbound messages from any channel,
finds or creates a conversation + lead, runs the AI engine, and sends the reply
back through the correct outbound channel.
"""
import logging
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.agent import Agent
from backend.models.conversation import Conversation, Message, ChannelType, MessageRole, ConversationStatus
from backend.models.lead import Lead, LeadStatus
from backend.engine.agent import run_agent
from backend.channels.outbound import send_reply

logger = logging.getLogger(__name__)


async def route_inbound_message(
    db: AsyncSession,
    agent: Agent,
    channel: ChannelType,
    sender_id: str,
    message_text: str,
    channel_message_id: str = "",
    initial_lead_data: Optional[dict] = None,
):
    """
    Main entry point for all inbound messages.
    1. Find or create conversation
    2. Find or create lead
    3. Store inbound message
    4. Run AI agent
    5. Store AI response
    6. Send reply through correct channel
    7. Sync to CRM if needed
    """
    # 1. Find existing conversation for this sender + agent + channel
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(
            Conversation.agent_id == agent.id,
            Conversation.channel == channel,
            Conversation.channel_conversation_id == sender_id,
            Conversation.status.in_([ConversationStatus.ACTIVE, ConversationStatus.QUALIFIED]),
        )
        .order_by(Conversation.updated_at.desc())
    )
    conversation = result.scalar_one_or_none()

    # 2. Find or create lead
    lead = None
    if conversation and conversation.lead_id:
        lead_result = await db.execute(select(Lead).where(Lead.id == conversation.lead_id))
        lead = lead_result.scalar_one_or_none()

    if not lead:
        lead = Lead(
            agent_id=agent.id,
            status=LeadStatus.NEW,
            source_channel=channel.value,
        )
        if initial_lead_data:
            for field, value in initial_lead_data.items():
                if hasattr(lead, field) and value:
                    setattr(lead, field, value)
        db.add(lead)
        await db.flush()

    # Create conversation if needed
    if not conversation:
        conversation = Conversation(
            agent_id=agent.id,
            lead_id=lead.id,
            channel=channel,
            channel_conversation_id=sender_id,
            status=ConversationStatus.ACTIVE,
        )
        db.add(conversation)
        await db.flush()
        # Need to load messages for the new conversation
        conversation.messages = []
    elif not conversation.lead_id:
        conversation.lead_id = lead.id

    # 3. Store inbound message
    inbound_msg = Message(
        conversation_id=conversation.id,
        role=MessageRole.LEAD,
        content=message_text,
        channel_message_id=channel_message_id,
    )
    db.add(inbound_msg)
    conversation.messages.append(inbound_msg)
    await db.flush()

    # 4. Run AI agent - load full agent config with pricing, service areas, objections
    agent_result = await db.execute(
        select(Agent)
        .options(
            selectinload(Agent.pricing),
            selectinload(Agent.service_areas),
            selectinload(Agent.objections),
        )
        .where(Agent.id == agent.id)
    )
    full_agent = agent_result.scalar_one()

    ai_response, lead_updates, actions = await run_agent(
        agent=full_agent,
        conversation=conversation,
        lead=lead,
        latest_message=message_text,
    )

    # 5. Apply any lead field updates the AI extracted
    if lead_updates:
        for field, value in lead_updates.items():
            if hasattr(lead, field) and value:
                setattr(lead, field, value)

    # 6. Store AI response
    outbound_msg = Message(
        conversation_id=conversation.id,
        role=MessageRole.AGENT,
        content=ai_response,
    )
    db.add(outbound_msg)

    # 7. Process actions (book appointment, update status, push to CRM, etc.)
    if actions:
        await _process_actions(db, agent, lead, conversation, actions)

    await db.flush()

    # 8. Send reply through the correct channel
    await send_reply(
        db=db,
        agent=full_agent,
        channel=channel,
        recipient_id=sender_id,
        message=ai_response,
    )

    logger.info(f"Processed message for agent={agent.id} channel={channel.value} sender={sender_id}")


async def _process_actions(
    db: AsyncSession,
    agent: Agent,
    lead: Lead,
    conversation: Conversation,
    actions: list[dict],
):
    """Process structured actions returned by the AI agent."""
    from backend.models.lead import Appointment
    from backend.integrations.crm import push_lead_to_crm
    from datetime import datetime

    for action in actions:
        action_type = action.get("type")

        if action_type == "update_lead_status":
            new_status = action.get("status")
            if new_status and hasattr(LeadStatus, new_status.upper()):
                lead.status = LeadStatus(new_status)

        elif action_type == "book_appointment":
            scheduled_at = action.get("scheduled_at")
            if scheduled_at:
                appt = Appointment(
                    lead_id=lead.id,
                    agent_id=agent.id,
                    scheduled_at=datetime.fromisoformat(scheduled_at),
                    duration_minutes=agent.appointment_duration_minutes,
                    service_type=action.get("service_type", lead.service_requested),
                )
                db.add(appt)
                lead.status = LeadStatus.BOOKED
                conversation.status = ConversationStatus.BOOKED

        elif action_type == "push_to_crm":
            await push_lead_to_crm(agent, lead)

        elif action_type == "hand_off":
            conversation.status = ConversationStatus.HANDED_OFF
            lead.status = LeadStatus.HANDED_OFF
