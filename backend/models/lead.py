import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base
import enum


class LeadStatus(str, enum.Enum):
    NEW = "new"
    QUALIFYING = "qualifying"
    QUOTED = "quoted"
    BOOKED = "booked"
    SUBSCRIBED = "subscribed"
    LOST = "lost"
    HANDED_OFF = "handed_off"


class Lead(Base):
    """A prospect captured through any channel."""
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    status: Mapped[LeadStatus] = mapped_column(Enum(LeadStatus), default=LeadStatus.NEW)

    # Contact info (collected progressively)
    name: Mapped[str] = mapped_column(String(255), default="")
    phone: Mapped[str] = mapped_column(String(20), default="")
    email: Mapped[str] = mapped_column(String(320), default="")
    address: Mapped[str] = mapped_column(String(500), default="")
    zip_code: Mapped[str] = mapped_column(String(10), default="")
    city: Mapped[str] = mapped_column(String(100), default="")
    state: Mapped[str] = mapped_column(String(50), default="")

    # Qualification data
    service_requested: Mapped[str] = mapped_column(String(255), default="")
    quoted_price: Mapped[str] = mapped_column(String(100), default="")
    custom_answers: Mapped[dict] = mapped_column(JSON, default=dict)  # answers to custom qualifying questions
    notes: Mapped[str] = mapped_column(Text, default="")

    # CRM sync
    crm_contact_id: Mapped[str] = mapped_column(String(100), default="")  # ID in external CRM
    crm_synced: Mapped[bool] = mapped_column(default=False)

    # Source tracking
    source_channel: Mapped[str] = mapped_column(String(50), default="")
    source_campaign: Mapped[str] = mapped_column(String(255), default="")
    utm_source: Mapped[str] = mapped_column(String(255), default="")
    utm_medium: Mapped[str] = mapped_column(String(255), default="")
    utm_campaign: Mapped[str] = mapped_column(String(255), default="")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    agent = relationship("Agent", back_populates="leads")
    conversations = relationship("Conversation", back_populates="lead")
    appointments = relationship("Appointment", back_populates="lead", cascade="all, delete-orphan")


class Appointment(Base):
    """Booked appointment for a lead."""
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    agent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(default=60)
    service_type: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(50), default="confirmed")  # confirmed, completed, cancelled, no_show
    notes: Mapped[str] = mapped_column(Text, default="")
    crm_event_id: Mapped[str] = mapped_column(String(100), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lead = relationship("Lead", back_populates="appointments")
