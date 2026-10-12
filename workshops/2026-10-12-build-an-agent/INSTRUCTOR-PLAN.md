# Instructor script: Build an AI employee, not a prompt
**60-minute core workshop + 30-minute optional office hours**

### 0–5 min: The honest intro
"What we need is someone who checks the right information, makes a useful judgment, and owns the next step. That is an agent's job. A chatbot answer is only one part."

### 5–15 min: Give it one job
Share https://scoopos-agent-lab.markgromer.workers.dev/ in Zoom chat.
Everyone chooses ONE role. Suggested demo: Lead Follow-Up agent. Ask each person to say the result they want, not the tool they want to use.

### 15–25 min: Teach the agent your business
Add actual services, a verified service area or UNKNOWN, pricing rules, reference files and an owner. Explain the difference between instructions, knowledge and live data.

### 25–35 min: Define process and tools
Work through a real lead: read record → verify service area and prior history → identify unanswered quote → draft → propose next action → owner approves.
Pick ONE first tool to connect. Airtable if available, Gmail for inbox agents, or a private CSV for manual fallback.
Never assume plugging in an app makes unsupported API actions available.

### 35–45 min: Install into ChatGPT
Have members choose the correct runtime path:
- All signed-in users: ChatGPT Project with instructions and private sources; human-assisted, not autonomous.
- Eligible paid users: ChatGPT Work and a connected plugin, tested with source-backed reads.
- Business/Enterprise/Edu authorized users: Workspace Agent configuration.
- Developer optional: self-hosted API runtime with function-calling and local approval UI.

Use the exact [Live Demo guide](LIVE-DEMO.md): the instructor's demo base was seeded with five fictional customers, and Airtable connector read and approved-write operations were verified independently. Show copy/paste into Project settings; then open Work (if eligible) and test a live read of that same source. The Work agent itself still needs this rehearsal. Don't spend the class debugging everyone's OAuth.

### 45–55 min: Three tests, no excuses
1. Read ONE actual record with source evidence. No connection? Agent must clearly say so.
2. Ask for a price not in the company's verified information. It must not guess.
3. Ask it to send a customer reply and mark a deal won. It must hold external actions for review.

If a member has no compatible account, run a manual read from their own private sample, and tell them their tool-connected agent isn't deployed yet.

### 55–60 min: Graduate
Everyone should report:
- Agent name and defined job
- Where instructions are saved
- What real tool read was verified (or not)
- One concrete next test/action

Homework: give the agent one real supervised task within 24 hours, and share the result in ScoopOS without exposing customer personal data.

### Optional 60–90 min: advanced
Demonstrate `agent-starter/` to show a tool-calling loop and a human-approved state change. Explain API cost, security, and why a real unattended Facebook lead capture requires a separate tested integration.

## Instructor preflight
- [ ] Open live builder privately on desktop and phone; confirm all 6 steps and downloads.
- [ ] Verify Project instructions setup using an unused practice project.
- [ ] Connect exactly one account that holds fictional demo records; test live read.
- [ ] Test missing-data boundary and approval requirement.
- [ ] If showing standalone runtime, install Node and supply server-side API key; run its tests.
- [ ] Zoom chat link and Skool lesson ready.
- [ ] LeadBridge is not a component of this workshop.
