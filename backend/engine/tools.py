"""
AI Agent tools - functions the LLM can call to take actions during a conversation.
These map to OpenAI function calling definitions.
"""

AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "update_lead_info",
            "description": "Update the lead's contact information as you learn it during the conversation. Call this whenever the customer shares their name, phone, email, address, zip code, or the service they need.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Customer's full name"},
                    "phone": {"type": "string", "description": "Customer's phone number"},
                    "email": {"type": "string", "description": "Customer's email address"},
                    "address": {"type": "string", "description": "Customer's street address"},
                    "zip_code": {"type": "string", "description": "Customer's ZIP code"},
                    "city": {"type": "string", "description": "Customer's city"},
                    "state": {"type": "string", "description": "Customer's state"},
                    "service_requested": {"type": "string", "description": "The service the customer is asking about"},
                    "notes": {"type": "string", "description": "Any additional notes about the customer's situation"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_service_area",
            "description": "Check if the customer's location is within the service area. Call this after learning their zip code or city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "zip_code": {"type": "string", "description": "ZIP code to check"},
                    "city": {"type": "string", "description": "City to check"},
                    "state": {"type": "string", "description": "State to check"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "provide_quote",
            "description": "Generate and present a price quote for the requested service. Call this when you have enough info to quote.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {"type": "string", "description": "The service being quoted"},
                    "quoted_price": {"type": "string", "description": "The price or price range to quote"},
                    "notes": {"type": "string", "description": "Any conditions or notes about the quote"},
                },
                "required": ["service_name", "quoted_price"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment for the customer. Call this when the customer confirms they want to schedule.",
            "parameters": {
                "type": "object",
                "properties": {
                    "scheduled_at": {
                        "type": "string",
                        "description": "ISO 8601 datetime for the appointment (e.g. 2025-03-15T10:00:00)",
                    },
                    "service_type": {"type": "string", "description": "The service being booked"},
                },
                "required": ["scheduled_at", "service_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "hand_off_to_human",
            "description": "Transfer the conversation to a human team member. Use this when the customer is upset, the question is outside your knowledge, or they specifically request a human.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {"type": "string", "description": "Why the handoff is needed"},
                },
                "required": ["reason"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "push_to_crm",
            "description": "Push the lead to the CRM system. Call this after booking an appointment or when the lead is fully qualified.",
            "parameters": {
                "type": "object",
                "properties": {
                    "trigger": {"type": "string", "description": "What triggered the CRM push (booked, qualified, etc.)"},
                },
                "required": [],
            },
        },
    },
]
