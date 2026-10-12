# ScoopOS Agent Starter — a working AI agent, not a prompt exercise

This is the optional developer extension for Bow Wow. It uses **the OpenAI Responses API with real function calls** to decide which lead tools to run. A local web interface shows what the model requested, the actual tool result, and any record change awaiting the owner's approval.

The starter runs **on your own computer, bound to 127.0.0.1**. It reads and updates **fictional local JSON lead data only**. It does not connect Facebook, Gmail, Quo, Airtable, Sweep & Go, or payment processors. Adding real business integrations requires separate security, privacy, authentication and testing.

## Requirements
- Node.js 20.6+ (with built-in `fetch` and `--env-file`)
- An OpenAI API key with available API balance (this is separate from a ChatGPT subscription)
- A model on your API account that supports Responses function calling. The default in `.env.example` is `gpt-4.1-mini`; change it if your account uses another supported model.

## Run

```bash
cd workshops/2026-10-12-build-an-agent/agent-starter
cp .env.example .env
# Put your real key in .env locally. Never commit .env or paste it into class.
npm test
npm start
```

Open **http://127.0.0.1:8788**.

On Windows PowerShell, use `Copy-Item .env.example .env` instead of `cp`. If you downloaded the repository ZIP, open a terminal in the extracted `agent-starter` folder.

## Demo
1. Click **Run AI agent** with the default prompt.
2. Expand **Actual tool call trace**. You should see `list_leads`, `get_lead`, or another supported tool invoked by the model.
3. Ask it to propose changing lead L-001 to `Needs Reply` with follow-up `2026-10-13`. The tool should return `awaiting_human_approval`.
4. See the pending diff on the page. Verify **L-001 has NOT changed**.
5. Click **Approve & save**. Only then does the local record change.
6. Refresh the page and confirm the record now reflects the change.

Try: "What exact weekly price can I quote Jamie?" The only acceptable answer is that the price is not verified.

## How it works

```
Your message
  ↓
OpenAI model (instructions + tool definitions)
  ↓   [function call chosen by model]
Server validates tool arguments
  ↓
Read local fictional lead OR queue proposed update
  ↓
Return tool result to model
  ↓
Model responds with evidence and next action
  ↓
[Separate owner approval button]
  ↓
Local JSON record changes and UI confirms
```

The **model chooses tool calls**, but the server owns all execution, validation and approvals. It cannot access any tool that isn't explicitly implemented server-side.

## What's here

- `agent.mjs`: Responses API tool-calling loop (no npm dependencies)
- `store.mjs`: demo lead records, validation and pending approval queue
- `server.mjs`: localhost HTTP UI and protected endpoints
- `agent-config.md`: editable agent instructions, policies and safety rules
- `ui.html`: readable local UI, tool trace, approvals
- `data/demo-leads.json`: fictional seed records
- `tests/agent.test.mjs`: automated tests, including "no write before approval"

## Important limitations
- **Local only; not production hardened.** Don't expose this HTTP server to the internet. It has no multi-user authentication or production rate limiting.
- Pending approvals are in memory. Restarting clears them; saved demo leads persist locally in `local-data/leads.json`.
- This starter does **not** carry over the full browser builder configuration automatically. Copy the generated **AGENT.md** content into `agent-config.md` after reviewing it for consistency with the available tools.
- `AGENT.md` may request integrations not in this code. Unsupported tools will NOT exist until you implement and test them.
- OpenAI API calls send prompt content and the fictional sample lead records returned by tools to the model provider; do not replace these with private customer data without designing appropriate privacy controls.
- This demo is single-session; history from prior questions is not automatically persisted. Each call relies on tools to read current data.

**No special access required for the core ChatGPT workshop**. Only do this extension if you want to learn how a *standalone* agent works in code.
