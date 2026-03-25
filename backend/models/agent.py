import uuid
from datetime import datetime
from sqlalchemy import String, Text, Float, Boolean, Integer, DateTime, ForeignKey, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


class Agent(Base):
    """
    An AI agent configuration belonging to a client.
    Each agent represents one 'bot' for a specific business/brand.
    """
    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Brand & voice configuration
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    business_type: Mapped[str] = mapped_column(String(100), nullable=False)  # plumbing, hvac, roofing, cleaning, etc.
    brand_voice: Mapped[str] = mapped_column(Text, default="")  # tone/style instructions
    greeting_message: Mapped[str] = mapped_column(Text, default="")
    fallback_message: Mapped[str] = mapped_column(Text, default="Let me connect you with our team.")

    # Guardrails
    guardrails: Mapped[str] = mapped_column(Text, default="")  # things the agent should never say/do
    max_discount_percent: Mapped[float] = mapped_column(Float, default=0.0)
    require_human_handoff_keywords: Mapped[list] = mapped_column(JSON, default=list)  # words that trigger human handoff

    # Scheduling
    booking_url: Mapped[str] = mapped_column(String(500), default="")  # external scheduling link
    availability_hours: Mapped[dict] = mapped_column(JSON, default=dict)  # {"mon": ["09:00-17:00"], ...}
    appointment_duration_minutes: Mapped[int] = mapped_column(Integer, default=60)

    # Channel connections
    twilio_phone_number: Mapped[str] = mapped_column(String(20), default="")
    meta_page_id: Mapped[str] = mapped_column(String(100), default="")
    meta_ig_account_id: Mapped[str] = mapped_column(String(100), default="")
    email_inbox: Mapped[str] = mapped_column(String(320), default="")

    # CRM integration
    crm_type: Mapped[str] = mapped_column(String(50), default="ghl")  # ghl, webhook, zapier
    crm_api_key: Mapped[str] = mapped_column(String(500), default="")
    crm_webhook_url: Mapped[str] = mapped_column(String(500), default="")
    crm_pipeline_id: Mapped[str] = mapped_column(String(100), default="")
    crm_stage_id: Mapped[str] = mapped_column(String(100), default="")

    # Custom fields the agent should collect
    required_lead_fields: Mapped[list] = mapped_column(JSON, default=lambda: ["name", "phone", "email", "address"])
    custom_questions: Mapped[list] = mapped_column(JSON, default=list)  # extra qualifying questions

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="agents")
    pricing = relationship("AgentPricing", back_populates="agent", cascade="all, delete-orphan")
    service_areas = relationship("AgentServiceArea", back_populates="agent", cascade="all, delete-orphan")
    objections = relationship("AgentObjection", back_populates="agent", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="agent", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="agent", cascade="all, delete-orphan")


class AgentPricing(Base):
    """Service pricing tiers configurable by the client."""
    __tablename__ = "agent_pricing"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    service_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    price_min: Mapped[float] = mapped_column(Float, nullable=False)
    price_max: Mapped[float] = mapped_column(Float, nullable=True)  # null = flat rate
    price_unit: Mapped[str] = mapped_column(String(50), default="per job")  # per job, per sqft, per hour, monthly
    is_subscription: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    agent = relationship("Agent", back_populates="pricing")


class AgentServiceArea(Base):
    """Zip codes / cities where the business operates."""
    __tablename__ = "agent_service_areas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    zip_code: Mapped[str] = mapped_column(String(10), default="")
    city: Mapped[str] = mapped_column(String(100), default="")
    state: Mapped[str] = mapped_column(String(50), default="")
    radius_miles: Mapped[float] = mapped_column(Float, default=0.0)  # 0 = exact match only

    agent = relationship("Agent", back_populates="service_areas")


class AgentObjection(Base):
    """Pre-written objection handling scripts."""
    __tablename__ = "agent_objections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    objection_trigger: Mapped[str] = mapped_column(String(255), nullable=False)  # "too expensive", "need to think about it"
    response_script: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    agent = relationship("Agent", back_populates="objections")
