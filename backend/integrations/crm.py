"""
CRM integration layer - pushes qualified leads to GoHighLevel or generic webhooks.
"""
import logging
import httpx

from backend.models.agent import Agent
from backend.models.lead import Lead

logger = logging.getLogger(__name__)


async def push_lead_to_crm(agent: Agent, lead: Lead):
    """Route lead to the correct CRM based on agent config."""
    if lead.crm_synced:
        logger.debug(f"Lead {lead.id} already synced to CRM")
        return

    crm_type = agent.crm_type or "ghl"

    try:
        if crm_type == "ghl":
            await _push_to_ghl(agent, lead)
        elif crm_type == "webhook":
            await _push_to_webhook(agent, lead)
        elif crm_type == "zapier":
            await _push_to_webhook(agent, lead)  # Zapier uses webhooks
        else:
            logger.warning(f"Unknown CRM type: {crm_type}")
            return

        lead.crm_synced = True
        logger.info(f"Lead {lead.id} pushed to {crm_type}")
    except Exception:
        logger.exception(f"Failed to push lead {lead.id} to {crm_type}")


async def _push_to_ghl(agent: Agent, lead: Lead):
    """Push lead to GoHighLevel as a contact."""
    api_key = agent.crm_api_key
    if not api_key:
        logger.warning("GHL API key not configured")
        return

    payload = {
        "firstName": lead.name.split(" ")[0] if lead.name else "",
        "lastName": " ".join(lead.name.split(" ")[1:]) if lead.name and " " in lead.name else "",
        "phone": lead.phone,
        "email": lead.email,
        "address1": lead.address,
        "city": lead.city,
        "state": lead.state,
        "postalCode": lead.zip_code,
        "source": f"Conduit - {lead.source_channel}",
        "tags": ["conduit-lead", lead.source_channel],
    }

    # Remove empty values
    payload = {k: v for k, v in payload.items() if v}

    async with httpx.AsyncClient() as client:
        # Create or update contact
        resp = await client.post(
            "https://rest.gohighlevel.com/v1/contacts/",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

        if resp.status_code in (200, 201):
            data = resp.json()
            contact_id = data.get("contact", {}).get("id", "")
            lead.crm_contact_id = contact_id

            # Add to pipeline if configured
            if agent.crm_pipeline_id and agent.crm_stage_id and contact_id:
                await client.post(
                    "https://rest.gohighlevel.com/v1/pipelines/opportunities/",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "pipelineId": agent.crm_pipeline_id,
                        "pipelineStageId": agent.crm_stage_id,
                        "contactId": contact_id,
                        "name": f"{lead.service_requested or 'New Lead'} - {lead.name}",
                        "status": "open",
                        "monetaryValue": lead.quoted_price.replace("$", "").replace(",", "").split("-")[0].strip() if lead.quoted_price else "0",
                    },
                )
        else:
            logger.error(f"GHL contact creation failed: {resp.status_code} - {resp.text}")


async def _push_to_webhook(agent: Agent, lead: Lead):
    """Push lead data to a generic webhook URL (works for Zapier, Make, n8n, etc.)."""
    webhook_url = agent.crm_webhook_url
    if not webhook_url:
        logger.warning("Webhook URL not configured")
        return

    payload = {
        "source": "conduit",
        "agent_id": str(lead.agent_id),
        "lead_id": str(lead.id),
        "status": lead.status.value if hasattr(lead.status, "value") else str(lead.status),
        "name": lead.name,
        "phone": lead.phone,
        "email": lead.email,
        "address": lead.address,
        "zip_code": lead.zip_code,
        "city": lead.city,
        "state": lead.state,
        "service_requested": lead.service_requested,
        "quoted_price": lead.quoted_price,
        "source_channel": lead.source_channel,
        "custom_answers": lead.custom_answers,
        "notes": lead.notes,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(webhook_url, json=payload, timeout=10.0)
        if resp.status_code >= 400:
            logger.error(f"Webhook push failed: {resp.status_code} - {resp.text}")
