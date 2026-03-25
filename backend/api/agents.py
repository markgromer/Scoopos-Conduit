import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database import get_db
from backend.api.auth import get_current_user
from backend.models.user import User
from backend.models.agent import Agent, AgentPricing, AgentServiceArea, AgentObjection
from backend.schemas.agent import (
    AgentCreate, AgentUpdate, AgentOut,
    PricingCreate, PricingOut,
    ServiceAreaCreate, ServiceAreaOut,
    ObjectionCreate, ObjectionOut,
)

router = APIRouter(prefix="/api/agents", tags=["agents"])


async def _get_agent_or_404(
    agent_id: uuid.UUID,
    user: User,
    db: AsyncSession,
) -> Agent:
    result = await db.execute(
        select(Agent)
        .options(
            selectinload(Agent.pricing),
            selectinload(Agent.service_areas),
            selectinload(Agent.objections),
        )
        .where(Agent.id == agent_id, Agent.owner_id == user.id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


# ── Agent CRUD ──

@router.get("/", response_model=list[AgentOut])
async def list_agents(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Agent)
        .options(
            selectinload(Agent.pricing),
            selectinload(Agent.service_areas),
            selectinload(Agent.objections),
        )
        .where(Agent.owner_id == user.id)
        .order_by(Agent.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=AgentOut, status_code=201)
async def create_agent(
    body: AgentCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = Agent(owner_id=user.id, **body.model_dump())
    db.add(agent)
    await db.flush()
    await db.refresh(agent, attribute_names=["pricing", "service_areas", "objections"])
    return agent


@router.get("/{agent_id}", response_model=AgentOut)
async def get_agent(
    agent_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _get_agent_or_404(agent_id, user, db)


@router.patch("/{agent_id}", response_model=AgentOut)
async def update_agent(
    agent_id: uuid.UUID,
    body: AgentUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = await _get_agent_or_404(agent_id, user, db)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(agent, field, value)
    await db.flush()
    await db.refresh(agent)
    return agent


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = await _get_agent_or_404(agent_id, user, db)
    await db.delete(agent)


# ── Pricing ──

@router.post("/{agent_id}/pricing", response_model=PricingOut, status_code=201)
async def add_pricing(
    agent_id: uuid.UUID,
    body: PricingCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_agent_or_404(agent_id, user, db)
    item = AgentPricing(agent_id=agent_id, **body.model_dump())
    db.add(item)
    await db.flush()
    return item


@router.delete("/{agent_id}/pricing/{pricing_id}", status_code=204)
async def remove_pricing(
    agent_id: uuid.UUID,
    pricing_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_agent_or_404(agent_id, user, db)
    result = await db.execute(
        select(AgentPricing).where(AgentPricing.id == pricing_id, AgentPricing.agent_id == agent_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Pricing item not found")
    await db.delete(item)


# ── Service Areas ──

@router.post("/{agent_id}/service-areas", response_model=ServiceAreaOut, status_code=201)
async def add_service_area(
    agent_id: uuid.UUID,
    body: ServiceAreaCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_agent_or_404(agent_id, user, db)
    item = AgentServiceArea(agent_id=agent_id, **body.model_dump())
    db.add(item)
    await db.flush()
    return item


@router.delete("/{agent_id}/service-areas/{area_id}", status_code=204)
async def remove_service_area(
    agent_id: uuid.UUID,
    area_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_agent_or_404(agent_id, user, db)
    result = await db.execute(
        select(AgentServiceArea).where(AgentServiceArea.id == area_id, AgentServiceArea.agent_id == agent_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Service area not found")
    await db.delete(item)


# ── Objections ──

@router.post("/{agent_id}/objections", response_model=ObjectionOut, status_code=201)
async def add_objection(
    agent_id: uuid.UUID,
    body: ObjectionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_agent_or_404(agent_id, user, db)
    item = AgentObjection(agent_id=agent_id, **body.model_dump())
    db.add(item)
    await db.flush()
    return item


@router.delete("/{agent_id}/objections/{objection_id}", status_code=204)
async def remove_objection(
    agent_id: uuid.UUID,
    objection_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_agent_or_404(agent_id, user, db)
    result = await db.execute(
        select(AgentObjection).where(AgentObjection.id == objection_id, AgentObjection.agent_id == agent_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Objection not found")
    await db.delete(item)
