import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ── Pricing ──
class PricingCreate(BaseModel):
    service_name: str
    description: str = ""
    price_min: float
    price_max: Optional[float] = None
    price_unit: str = "per job"
    is_subscription: bool = False
    sort_order: int = 0


class PricingOut(PricingCreate):
    id: uuid.UUID
    model_config = {"from_attributes": True}


# ── Service Area ──
class ServiceAreaCreate(BaseModel):
    zip_code: str = ""
    city: str = ""
    state: str = ""
    radius_miles: float = 0.0


class ServiceAreaOut(ServiceAreaCreate):
    id: uuid.UUID
    model_config = {"from_attributes": True}


# ── Objections ──
class ObjectionCreate(BaseModel):
    objection_trigger: str
    response_script: str
    sort_order: int = 0


class ObjectionOut(ObjectionCreate):
    id: uuid.UUID
    model_config = {"from_attributes": True}


# ── Agent ──
class AgentCreate(BaseModel):
    name: str
    business_name: str
    business_type: str
    brand_voice: str = ""
    greeting_message: str = ""
    fallback_message: str = "Let me connect you with our team."
    guardrails: str = ""
    max_discount_percent: float = 0.0
    require_human_handoff_keywords: list[str] = []
    booking_url: str = ""
    availability_hours: dict = {}
    appointment_duration_minutes: int = 60
    twilio_phone_number: str = ""
    meta_page_id: str = ""
    meta_ig_account_id: str = ""
    email_inbox: str = ""
    crm_type: str = "ghl"
    crm_api_key: str = ""
    crm_webhook_url: str = ""
    crm_pipeline_id: str = ""
    crm_stage_id: str = ""
    required_lead_fields: list[str] = ["name", "phone", "email", "address"]
    custom_questions: list[str] = []


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    brand_voice: Optional[str] = None
    greeting_message: Optional[str] = None
    fallback_message: Optional[str] = None
    guardrails: Optional[str] = None
    max_discount_percent: Optional[float] = None
    require_human_handoff_keywords: Optional[list[str]] = None
    booking_url: Optional[str] = None
    availability_hours: Optional[dict] = None
    appointment_duration_minutes: Optional[int] = None
    twilio_phone_number: Optional[str] = None
    meta_page_id: Optional[str] = None
    meta_ig_account_id: Optional[str] = None
    email_inbox: Optional[str] = None
    crm_type: Optional[str] = None
    crm_api_key: Optional[str] = None
    crm_webhook_url: Optional[str] = None
    crm_pipeline_id: Optional[str] = None
    crm_stage_id: Optional[str] = None
    required_lead_fields: Optional[list[str]] = None
    custom_questions: Optional[list[str]] = None


class AgentOut(BaseModel):
    id: uuid.UUID
    name: str
    is_active: bool
    business_name: str
    business_type: str
    brand_voice: str
    greeting_message: str
    fallback_message: str
    guardrails: str
    max_discount_percent: float
    require_human_handoff_keywords: list
    booking_url: str
    availability_hours: dict
    appointment_duration_minutes: int
    twilio_phone_number: str
    meta_page_id: str
    meta_ig_account_id: str
    email_inbox: str
    crm_type: str
    crm_webhook_url: str
    crm_pipeline_id: str
    crm_stage_id: str
    required_lead_fields: list
    custom_questions: list
    created_at: datetime
    updated_at: datetime
    pricing: list[PricingOut] = []
    service_areas: list[ServiceAreaOut] = []
    objections: list[ObjectionOut] = []

    model_config = {"from_attributes": True}
