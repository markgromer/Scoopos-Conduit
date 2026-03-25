import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database import get_db
from backend.api.auth import get_current_user
from backend.models.user import User
from backend.models.agent import Agent
from backend.models.lead import Lead, LeadStatus, Appointment
from backend.models.conversation import Conversation, ConversationStatus
from backend.schemas.conversation import ConversationOut, ConversationDetail, MessageOut, LeadOut, AppointmentOut

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
async def dashboard_stats(
    agent_id: uuid.UUID = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """High-level stats for the dashboard home screen."""
    # Verify ownership
    result = await db.execute(select(Agent).where(Agent.id == agent_id, Agent.owner_id == user.id))
    agent = result.scalar_one_or_none()
    if not agent:
        return {"error": "Agent not found"}

    total_leads = await db.scalar(
        select(func.count()).select_from(Lead).where(Lead.agent_id == agent_id)
    )
    booked = await db.scalar(
        select(func.count()).select_from(Lead).where(Lead.agent_id == agent_id, Lead.status == LeadStatus.BOOKED)
    )
    active_convos = await db.scalar(
        select(func.count()).select_from(Conversation).where(
            Conversation.agent_id == agent_id, Conversation.status == ConversationStatus.ACTIVE
        )
    )
    total_appointments = await db.scalar(
        select(func.count()).select_from(Appointment).where(Appointment.agent_id == agent_id)
    )

    return {
        "total_leads": total_leads or 0,
        "booked_leads": booked or 0,
        "active_conversations": active_convos or 0,
        "total_appointments": total_appointments or 0,
        "conversion_rate": round((booked / total_leads * 100) if total_leads else 0, 1),
    }


@router.get("/leads", response_model=list[LeadOut])
async def list_leads(
    agent_id: uuid.UUID = Query(...),
    status: str = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Lead).where(Lead.agent_id == agent_id)
    if status:
        query = query.where(Lead.status == status)
    query = query.order_by(Lead.created_at.desc()).limit(100)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/conversations", response_model=list[ConversationOut])
async def list_conversations(
    agent_id: uuid.UUID = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.agent_id == agent_id)
        .order_by(Conversation.updated_at.desc())
        .limit(100)
    )
    return result.scalars().all()


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == conversation_id)
    )
    convo = result.scalar_one_or_none()
    if not convo:
        return {"error": "Conversation not found"}
    return convo


@router.get("/appointments", response_model=list[AppointmentOut])
async def list_appointments(
    agent_id: uuid.UUID = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Appointment)
        .where(Appointment.agent_id == agent_id)
        .order_by(Appointment.scheduled_at.desc())
        .limit(100)
    )
    return result.scalars().all()
