import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base
import enum


class ChannelType(str, enum.Enum):
    SMS = "sms"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    EMAIL = "email"
    LEAD_FORM = "lead_form"
    WEB_CHAT = "web_chat"


class MessageRole(str, enum.Enum):
    LEAD = "lead"        # message from the prospect
    AGENT = "agent"      # AI agent response
    SYSTEM = "system"    # internal notes / handoff markers


class ConversationStatus(str, enum.Enum):
    ACTIVE = "active"
    QUALIFIED = "qualified"
    BOOKED = "booked"
    LOST = "lost"
    HANDED_OFF = "handed_off"


class Conversation(Base):
    """A conversation thread between an AI agent and a lead across any channel."""
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    lead_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True)
    channel: Mapped[ChannelType] = mapped_column(Enum(ChannelType), nullable=False)
    channel_conversation_id: Mapped[str] = mapped_column(String(500), default="")  # platform-specific thread id
    status: Mapped[ConversationStatus] = mapped_column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    agent = relationship("Agent", back_populates="conversations")
    lead = relationship("Lead", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    """Individual message within a conversation."""
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    channel_message_id: Mapped[str] = mapped_column(String(500), default="")  # platform-specific message id
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")
