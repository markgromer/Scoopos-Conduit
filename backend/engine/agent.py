"""
Core AI agent - runs the OpenAI conversation with function calling,
processes tool calls, and returns the response + any actions to take.
"""
import json
import logging
from typing import Optional
from openai import AsyncOpenAI

from backend.config import settings
from backend.models.agent import Agent
from backend.models.conversation import Conversation, MessageRole
from backend.models.lead import Lead
from backend.engine.prompts import build_system_prompt
from backend.engine.tools import AGENT_TOOLS

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=settings.openai_api_key)


async def run_agent(
    agent: Agent,
    conversation: Conversation,
    lead: Lead,
    latest_message: str,
) -> tuple[str, Optional[dict], Optional[list[dict]]]:
    """
    Run the AI agent for a single turn of conversation.

    Returns:
        (response_text, lead_updates, actions)
        - response_text: the message to send back to the lead
        - lead_updates: dict of lead fields to update (or None)
        - actions: list of action dicts to process (or None)
    """
    system_prompt = build_system_prompt(agent, lead)

    # Build message history from conversation
    messages = [{"role": "system", "content": system_prompt}]

    # Include greeting if this is the first message
    if len(conversation.messages) <= 1 and agent.greeting_message:
        messages.append({"role": "assistant", "content": agent.greeting_message})

    # Add conversation history (limit to last 40 messages to stay within context)
    for msg in conversation.messages[-40:]:
        if msg.role == MessageRole.LEAD:
            messages.append({"role": "user", "content": msg.content})
        elif msg.role == MessageRole.AGENT:
            messages.append({"role": "assistant", "content": msg.content})

    # Call OpenAI with function calling
    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            tools=AGENT_TOOLS,
            tool_choice="auto",
            temperature=0.7,
            max_tokens=1000,
        )
    except Exception:
        logger.exception("OpenAI API call failed")
        return agent.fallback_message, None, None

    choice = response.choices[0]
    lead_updates = {}
    actions = []

    # Process tool calls if any
    if choice.message.tool_calls:
        # Add the assistant message with tool calls
        messages.append(choice.message.model_dump())

        for tool_call in choice.message.tool_calls:
            fn_name = tool_call.function.name
            try:
                fn_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                fn_args = {}

            tool_result = _execute_tool(fn_name, fn_args, agent, lead, lead_updates, actions)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result),
            })

        # Get the final response after tool execution
        try:
            followup = await client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )
            response_text = followup.choices[0].message.content or agent.fallback_message
        except Exception:
            logger.exception("OpenAI followup call failed")
            response_text = agent.fallback_message
    else:
        response_text = choice.message.content or agent.fallback_message

    # Check for human handoff keywords
    if agent.require_human_handoff_keywords:
        lower_msg = latest_message.lower()
        for keyword in agent.require_human_handoff_keywords:
            if keyword.lower() in lower_msg:
                actions.append({"type": "hand_off", "reason": f"Keyword triggered: {keyword}"})
                break

    return response_text, lead_updates or None, actions or None


def _execute_tool(
    fn_name: str,
    fn_args: dict,
    agent: Agent,
    lead: Lead,
    lead_updates: dict,
    actions: list[dict],
) -> dict:
    """Execute a tool call and return the result as a dict for the AI."""

    if fn_name == "update_lead_info":
        # Merge updates
        for key, value in fn_args.items():
            if value:
                lead_updates[key] = value
        return {"status": "ok", "message": "Lead info updated."}

    elif fn_name == "check_service_area":
        return _check_service_area(fn_args, agent)

    elif fn_name == "provide_quote":
        lead_updates["service_requested"] = fn_args.get("service_name", "")
        lead_updates["quoted_price"] = fn_args.get("quoted_price", "")
        actions.append({"type": "update_lead_status", "status": "quoted"})
        return {
            "status": "ok",
            "service": fn_args.get("service_name"),
            "price": fn_args.get("quoted_price"),
            "notes": fn_args.get("notes", ""),
        }

    elif fn_name == "book_appointment":
        actions.append({
            "type": "book_appointment",
            "scheduled_at": fn_args.get("scheduled_at"),
            "service_type": fn_args.get("service_type", ""),
        })
        actions.append({"type": "push_to_crm", "trigger": "booked"})
        return {"status": "ok", "message": "Appointment booked successfully."}

    elif fn_name == "hand_off_to_human":
        actions.append({"type": "hand_off", "reason": fn_args.get("reason", "Customer request")})
        return {"status": "ok", "message": "Transferring to a team member."}

    elif fn_name == "push_to_crm":
        actions.append({"type": "push_to_crm", "trigger": fn_args.get("trigger", "manual")})
        return {"status": "ok", "message": "Lead pushed to CRM."}

    return {"status": "error", "message": f"Unknown tool: {fn_name}"}


def _check_service_area(args: dict, agent: Agent) -> dict:
    """Check if the given location is within the agent's service area."""
    if not agent.service_areas:
        return {"in_service_area": True, "message": "Service area not configured, all locations accepted."}

    zip_code = args.get("zip_code", "").strip()
    city = args.get("city", "").strip().lower()
    state = args.get("state", "").strip().lower()

    for sa in agent.service_areas:
        # Exact ZIP match
        if zip_code and sa.zip_code and sa.zip_code == zip_code:
            return {"in_service_area": True, "message": f"Yes, we service ZIP code {zip_code}."}

        # City + state match
        if city and sa.city and sa.city.lower() == city:
            if not sa.state or sa.state.lower() == state:
                return {"in_service_area": True, "message": f"Yes, we service {city.title()}."}

    return {
        "in_service_area": False,
        "message": "Unfortunately, that location is outside our current service area.",
    }
