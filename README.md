# Conduit

AI-powered multi-channel lead conversion platform for service businesses. Connects to Facebook Messenger, Instagram, SMS, email, and web lead forms. Qualifies leads, provides quotes, handles objections, books appointments, and pushes everything into your CRM.

## Architecture

```
Channels (FB, IG, SMS, Email, Lead Forms)
        | webhooks
   Channel Router -> AI Agent Engine (OpenAI function calling)
        |                   |
  Conversation DB     Agent Tools (quote, book, qualify, hand off)
        |                   |
   CRM Push (GHL, webhooks, Zapier)
        |
   Client Dashboard (React + Tailwind)
```

### Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy (async), PostgreSQL
- **AI Engine:** OpenAI GPT-4o with function calling
- **Queue:** Redis + Celery for background tasks
- **SMS:** Twilio
- **Social:** Meta Graph API (Facebook Messenger + Instagram)
- **Email:** SendGrid Inbound Parse
- **CRM:** GoHighLevel API, generic webhooks (Zapier, Make, n8n)
- **Frontend:** React 19, Vite, Tailwind CSS, Zustand
- **Deploy:** Docker Compose

## Project Structure

```
backend/
  main.py           - FastAPI app entry point
  config.py         - Environment settings
  database.py       - Async PostgreSQL connection
  models/           - SQLAlchemy models (User, Agent, Conversation, Lead, Appointment)
  schemas/          - Pydantic request/response schemas
  api/
    auth.py         - JWT auth (register, login, me)
    agents.py       - Agent CRUD + pricing, service areas, objections
    dashboard.py    - Stats, leads, conversations, appointments
    webhooks.py     - Inbound webhooks for all channels
  channels/
    router.py       - Central message router (find/create convo + lead, run AI, send reply)
    outbound.py     - Send replies via SMS, FB, IG, email
  engine/
    agent.py        - Core AI agent logic with OpenAI function calling
    prompts.py      - Dynamic system prompt builder from agent config
    tools.py        - OpenAI tool definitions (update_lead, check_area, quote, book, handoff)
  integrations/
    crm.py          - GHL contact creation + webhook push
  workers/
    tasks.py        - Celery background tasks (follow-ups, CRM sync)

frontend/
  src/
    api/client.ts   - Typed API client
    stores/auth.ts  - Zustand auth store
    pages/
      Login.tsx     - Login / register
      Dashboard.tsx - Agent selector, stats cards, create agent
      AgentConfig.tsx - 7-tab agent training UI (voice, pricing, areas, objections, channels, CRM, advanced)
      Leads.tsx     - Lead table with filters
      Conversations.tsx - Conversation viewer with message thread
      Settings.tsx  - Account info, API endpoints
```

## Setup

### 1. Prerequisites

- Docker + Docker Compose (or Python 3.12 + PostgreSQL + Redis locally)
- Node.js 20+
- OpenAI API key
- Twilio account (for SMS)
- Meta developer app (for FB/IG)
- SendGrid account (for email)

### 2. Environment

```bash
cp .env.example .env
# Fill in your API keys
```

### 3. Start with Docker

```bash
docker compose up -d
```

This starts PostgreSQL, Redis, the API server, and the Celery worker.

### 4. Start without Docker

```bash
# Backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn backend.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### 5. Create your first agent

1. Open http://localhost:5173
2. Register an account
3. Click "New Agent" - enter your business name and type
4. Configure the agent with the tabbed interface:
   - **Brand Voice:** Set tone, greeting message, personality
   - **Pricing:** Add your service pricing tiers
   - **Service Areas:** Add zip codes, cities, or radius-based areas
   - **Objections:** Teach the AI how to handle common pushback
   - **Channels:** Connect SMS number, Facebook page, IG account, email inbox
   - **CRM:** Connect GoHighLevel or set up webhook push
   - **Advanced:** Guardrails, handoff keywords, custom questions, booking URL

### 6. Connect channels

**SMS (Twilio):**
Set your Twilio webhook URL to `https://yourdomain.com/api/webhooks/sms`

**Facebook Messenger:**
Set your Meta webhook URL to `https://yourdomain.com/api/webhooks/meta`
Subscribe to `messages` events

**Instagram:**
Same Meta webhook - use your IG-connected page

**Email:**
Configure SendGrid Inbound Parse to forward to `https://yourdomain.com/api/webhooks/email`

**Lead Forms:**
POST JSON to `https://yourdomain.com/api/webhooks/lead-form/{agent_id}`

```json
{
  "name": "John Smith",
  "phone": "555-123-4567",
  "email": "john@example.com",
  "service": "Drain cleaning",
  "address": "123 Main St",
  "message": "My kitchen sink is clogged"
}
```

## Deploy on Render (Blueprint)

This repo includes a Render Blueprint file at the repo root: `render.yaml`.

1. In Render, click **New** -> **Blueprint** and connect the GitHub repo.
2. Render should detect `render.yaml` and show you the resources it will create:
   - `conduit-api` (web service)
   - `conduit-worker` (background worker)
   - `conduit-redis` (Render Key Value)
   - `conduit-db` (Render Postgres)
3. During the setup wizard, enter values for any environment variables marked `sync: false` (OpenAI, Twilio, Meta, SendGrid, GHL).
4. Deploy.

Notes:
- The Blueprint uses a supported Postgres plan (currently `basic-256mb`).
- The backend normalizes Render's `DATABASE_URL` into an async SQLAlchemy URL at runtime.
- The React dashboard is built during deploy and served by the same FastAPI service.

## How It Works

1. A message arrives via any channel webhook
2. The **Channel Router** finds (or creates) a conversation and lead record
3. The **AI Agent Engine** builds a dynamic system prompt from the agent's configuration (brand voice, pricing, service areas, objection scripts, guardrails)
4. OpenAI processes the conversation with **function calling** - the AI can call tools like `update_lead_info`, `check_service_area`, `provide_quote`, `book_appointment`, or `hand_off_to_human`
5. Tool results feed back into the AI for a natural response
6. The response is sent back through the correct **outbound channel**
7. Lead data and conversation history persist in PostgreSQL
8. Qualified/booked leads automatically push to the **CRM**

## Database Migrations

```bash
# Generate a migration after model changes
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/auth/register | Create account |
| POST | /api/auth/login | Get JWT token |
| GET | /api/auth/me | Current user |
| GET/POST | /api/agents/ | List / create agents |
| GET/PATCH/DELETE | /api/agents/:id | Get / update / delete agent |
| POST/DELETE | /api/agents/:id/pricing | Manage pricing |
| POST/DELETE | /api/agents/:id/service-areas | Manage service areas |
| POST/DELETE | /api/agents/:id/objections | Manage objection handlers |
| GET | /api/dashboard/stats | Agent stats |
| GET | /api/dashboard/leads | Lead list |
| GET | /api/dashboard/conversations | Conversation list |
| GET | /api/dashboard/conversations/:id | Conversation detail with messages |
| GET | /api/dashboard/appointments | Appointment list |
| POST | /api/webhooks/sms | Twilio inbound |
| GET/POST | /api/webhooks/meta | Meta (FB + IG) webhook |
| POST | /api/webhooks/email | SendGrid inbound |
| POST | /api/webhooks/lead-form/:agent_id | Generic lead form |
