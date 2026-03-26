import uuid
import logging
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from itsdangerous import BadSignature, URLSafeSerializer

from backend.config import settings
from backend.database import get_db
from backend.api.auth import get_current_user
from backend.models.user import User
from backend.models.agent import Agent, AgentPricing, AgentServiceArea, AgentObjection
from backend.models.meta_connection import AgentMetaConnection, AgentMetaConnectSession
from backend.schemas.agent import (
    AgentCreate, AgentUpdate, AgentOut,
    PricingCreate, PricingOut,
    ServiceAreaCreate, ServiceAreaOut,
    ObjectionCreate, ObjectionOut,
)

router = APIRouter(prefix="/api/agents", tags=["agents"])
logger = logging.getLogger(__name__)


def _meta_connect_serializer() -> URLSafeSerializer:
    return URLSafeSerializer(settings.secret_key, salt="conduit-meta-connect")


def _facebook_client_id() -> str:
    return settings.facebook_client_id or settings.meta_app_id


def _facebook_client_secret() -> str:
    return settings.facebook_client_secret or settings.meta_app_secret


def _make_meta_connect_state(agent_id: uuid.UUID, user_id: uuid.UUID) -> str:
    return _meta_connect_serializer().dumps(
        {
            "agent_id": str(agent_id),
            "user_id": str(user_id),
            "ts": int(time.time()),
        }
    )


def _parse_meta_connect_state(state: str) -> tuple[uuid.UUID, uuid.UUID]:
    try:
        data = _meta_connect_serializer().loads(state)
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid Meta connect state")

    ts = int(data.get("ts") or 0)
    if ts <= 0 or (time.time() - ts) > 10 * 60:
        raise HTTPException(status_code=400, detail="Meta connect state expired")

    try:
        return uuid.UUID(str(data["agent_id"])), uuid.UUID(str(data["user_id"]))
    except (KeyError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid Meta connect state")


def _agent_channels_url(agent_id: uuid.UUID, **params: str | int) -> str:
    clean_params = {key: str(value) for key, value in params.items() if value is not None and value != ""}
    clean_params["tab"] = "channels"
    query = urlencode(clean_params)
    return f"/agent/{agent_id}?{query}"


async def _subscribe_page_to_app(page_id: str, page_access_token: str) -> None:
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(
            f"https://graph.facebook.com/v19.0/{page_id}/subscribed_apps",
            params={
                "access_token": page_access_token,
                "subscribed_fields": "messages,messaging_postbacks",
            },
        )
        if resp.status_code >= 400:
            logger.error("Meta page subscribe failed: %s", resp.text)
            raise HTTPException(
                status_code=400,
                detail="Facebook authorized successfully, but page subscription failed",
            )


async def _upsert_meta_connection(
    db: AsyncSession,
    agent: Agent,
    owner_id: uuid.UUID,
    page_data: dict,
) -> AgentMetaConnection:
    page_id = str(page_data.get("id") or "")
    page_name = str(page_data.get("name") or "")
    page_access_token = str(page_data.get("access_token") or "")
    ig_account = page_data.get("instagram_business_account") or {}
    ig_account_id = str(ig_account.get("id") or "")
    ig_username = str(ig_account.get("username") or "")

    if not page_id or not page_access_token:
        raise HTTPException(status_code=400, detail="Facebook did not return a usable Page connection")

    await _subscribe_page_to_app(page_id, page_access_token)

    result = await db.execute(
        select(AgentMetaConnection).where(AgentMetaConnection.agent_id == agent.id)
    )
    connection = result.scalar_one_or_none()
    if not connection:
        connection = AgentMetaConnection(agent_id=agent.id, owner_id=owner_id, page_id=page_id, page_access_token=page_access_token)
        db.add(connection)

    connection.owner_id = owner_id
    connection.page_id = page_id
    connection.page_name = page_name
    connection.page_access_token = page_access_token
    connection.ig_account_id = ig_account_id
    connection.ig_username = ig_username

    agent.meta_page_id = page_id
    agent.meta_ig_account_id = ig_account_id
    await db.flush()
    return connection


async def _get_meta_connection(agent_id: uuid.UUID, db: AsyncSession) -> AgentMetaConnection | None:
    result = await db.execute(
        select(AgentMetaConnection).where(AgentMetaConnection.agent_id == agent_id)
    )
    return result.scalar_one_or_none()


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


@router.get("/{agent_id}/meta/connect/start")
async def start_meta_connect(
    agent_id: uuid.UUID,
    request: Request,
    return_url: bool = False,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_agent_or_404(agent_id, user, db)

    client_id = _facebook_client_id()
    client_secret = _facebook_client_secret()
    if not client_id or not client_secret:
        raise HTTPException(status_code=503, detail="Facebook is not configured")

    redirect_uri = str(request.url_for("meta_connect_callback"))
    state = _make_meta_connect_state(agent_id, user.id)
    url = httpx.URL("https://www.facebook.com/v19.0/dialog/oauth").copy_merge_params(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "pages_show_list,pages_manage_metadata,pages_messaging,instagram_basic,instagram_manage_messages,business_management",
            "state": state,
        }
    )
    if return_url:
        return {"url": str(url)}
    return RedirectResponse(str(url), status_code=302)


@router.get("/meta/connect/callback", name="meta_connect_callback")
async def meta_connect_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_reason: str | None = None,
    error_description: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    if state and (error or error_reason or error_description):
        try:
            agent_id, _user_id = _parse_meta_connect_state(state)
            message = error_reason or error or error_description or "facebook_oauth_failed"
            return RedirectResponse(_agent_channels_url(agent_id, meta_error=message), status_code=302)
        except HTTPException:
            raise HTTPException(status_code=400, detail=error_description or error_reason or error or "Meta connect failed")

    if not code or not state:
        raise HTTPException(status_code=400, detail="Meta connect did not return an authorization code")

    agent_id, user_id = _parse_meta_connect_state(state)

    result = await db.execute(
        select(Agent).where(Agent.id == agent_id, Agent.owner_id == user_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    client_id = _facebook_client_id()
    client_secret = _facebook_client_secret()
    if not client_id or not client_secret:
        return RedirectResponse(_agent_channels_url(agent_id, meta_error="facebook_not_configured"), status_code=302)

    redirect_uri = str(request.url_for("meta_connect_callback"))

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            token_resp = await client.get(
                "https://graph.facebook.com/v19.0/oauth/access_token",
                params={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "code": code,
                },
            )
            token_resp.raise_for_status()
            access_token = token_resp.json().get("access_token")
            if not access_token:
                return RedirectResponse(_agent_channels_url(agent_id, meta_error="facebook_token_failed"), status_code=302)

            pages_resp = await client.get(
                "https://graph.facebook.com/v19.0/me/accounts",
                params={
                    "fields": "id,name,access_token,instagram_business_account{id,username}",
                    "access_token": access_token,
                },
            )
            pages_resp.raise_for_status()
            pages = pages_resp.json().get("data", [])

        if not pages:
            return RedirectResponse(_agent_channels_url(agent_id, meta_error="no_pages_found"), status_code=302)

        if len(pages) == 1:
            await _upsert_meta_connection(db, agent, user_id, pages[0])
            return RedirectResponse(_agent_channels_url(agent_id, meta_connected=1), status_code=302)

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        session = AgentMetaConnectSession(
            agent_id=agent.id,
            owner_id=user_id,
            pages_json=pages,
            expires_at=expires_at,
        )
        db.add(session)
        await db.flush()
        return RedirectResponse(_agent_channels_url(agent_id, meta_session=session.id), status_code=302)
    except httpx.HTTPError:
        logger.exception("Meta connect callback failed")
        return RedirectResponse(_agent_channels_url(agent_id, meta_error="facebook_request_failed"), status_code=302)
    except HTTPException as exc:
        logger.exception("Meta connect callback failed")
        return RedirectResponse(_agent_channels_url(agent_id, meta_error=exc.detail), status_code=302)
    except Exception:
        logger.exception("Meta connect callback failed")
        return RedirectResponse(_agent_channels_url(agent_id, meta_error="facebook_connect_failed"), status_code=302)


@router.get("/{agent_id}/meta/connect/status")
async def get_meta_connect_status(
    agent_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = await _get_agent_or_404(agent_id, user, db)
    connection = await _get_meta_connection(agent.id, db)
    if not connection:
        return {"connected": False}

    return {
        "connected": True,
        "page_id": connection.page_id,
        "page_name": connection.page_name,
        "ig_account_id": connection.ig_account_id,
        "ig_username": connection.ig_username,
        "connected_at": connection.created_at,
    }


@router.get("/{agent_id}/meta/connect/session/{session_id}")
async def get_meta_connect_session(
    agent_id: uuid.UUID,
    session_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_agent_or_404(agent_id, user, db)
    result = await db.execute(
        select(AgentMetaConnectSession).where(
            AgentMetaConnectSession.id == session_id,
            AgentMetaConnectSession.agent_id == agent_id,
            AgentMetaConnectSession.owner_id == user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Meta connect session not found")
    if session.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Meta connect session expired")

    pages = []
    for page in session.pages_json or []:
        ig_account = page.get("instagram_business_account") or {}
        pages.append(
            {
                "id": str(page.get("id") or ""),
                "name": str(page.get("name") or ""),
                "ig_account_id": str(ig_account.get("id") or ""),
                "ig_username": str(ig_account.get("username") or ""),
            }
        )
    return {"pages": pages}


@router.post("/{agent_id}/meta/connect/complete")
async def complete_meta_connect(
    agent_id: uuid.UUID,
    body: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = await _get_agent_or_404(agent_id, user, db)
    try:
        session_id = uuid.UUID(str(body.get("session_id") or ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Meta connect session")

    page_id = str(body.get("page_id") or "")
    if not page_id:
        raise HTTPException(status_code=400, detail="Missing page id")

    result = await db.execute(
        select(AgentMetaConnectSession).where(
            AgentMetaConnectSession.id == session_id,
            AgentMetaConnectSession.agent_id == agent_id,
            AgentMetaConnectSession.owner_id == user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Meta connect session not found")
    if session.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Meta connect session expired")

    selected_page = None
    for page in session.pages_json or []:
        if str(page.get("id") or "") == page_id:
            selected_page = page
            break
    if not selected_page:
        raise HTTPException(status_code=404, detail="Facebook page not found in session")

    connection = await _upsert_meta_connection(db, agent, user.id, selected_page)
    await db.delete(session)
    return {
        "connected": True,
        "page_id": connection.page_id,
        "page_name": connection.page_name,
        "ig_account_id": connection.ig_account_id,
        "ig_username": connection.ig_username,
    }


@router.delete("/{agent_id}/meta/connect")
async def disconnect_meta_connect(
    agent_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = await _get_agent_or_404(agent_id, user, db)
    connection = await _get_meta_connection(agent.id, db)
    if connection:
        await db.delete(connection)
    agent.meta_page_id = ""
    agent.meta_ig_account_id = ""
    await db.flush()
    return {"connected": False}


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
