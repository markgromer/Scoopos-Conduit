import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ConversationOut(BaseModel):
    id: uuid.UUID
    agent_id: uuid.UUID
    lead_id: Optional[uuid.UUID] = None
    channel: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageOut(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationDetail(ConversationOut):
    messages: list[MessageOut] = []


class LeadOut(BaseModel):
    id: uuid.UUID
    agent_id: uuid.UUID
    status: str
    name: str
    phone: str
    email: str
    address: str
    zip_code: str
    city: str
    state: str
    service_requested: str
    quoted_price: str
    custom_answers: dict
    notes: str
    source_channel: str
    crm_synced: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AppointmentOut(BaseModel):
    id: uuid.UUID
    lead_id: uuid.UUID
    agent_id: uuid.UUID
    scheduled_at: datetime
    duration_minutes: int
    service_type: str
    status: str
    notes: str
    created_at: datetime

    model_config = {"from_attributes": True}
