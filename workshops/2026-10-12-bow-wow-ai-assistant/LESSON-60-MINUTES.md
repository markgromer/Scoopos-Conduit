# Instructor lesson: Stop chatting with AI. Give it a real job.

**Monday, October 12, 2026 | 4:00 PM Arizona time**
**ScoopOS / Poop Scoop Syndicate Weekly Bow Wow**
**Core lesson: 60 minutes + optional 30-minute office hours**

## The promise

By the end of this session, attendees can show:
1. One simple lead board with fictional practice customers.
2. One "business brain" telling ChatGPT what is true and what it must never guess.
3. One prioritized lead, one approved reply draft, and one follow-up date.

**Not promised:** Automated Facebook collection, LeadBridge, automatic texting, background sync, or autonomous CRM changes. Those are later lessons after tested integrations.

## 0:00–0:08 · Hook: Where do leads go to die?

**Say:** "You don't need a new AI business. You need the leads you already paid for to stop slipping through the cracks."

Ask: "When someone asks for a quote and isn't ready today, where does their name go? What tells you when to follow up?"

Show a simple fictional situation:
- Jamie requests weekly service Saturday.
- They have two dogs; no verified ZIP or quote.
- The owner is busy and forgets to follow up.
- AI cannot sell what the owner never responds to.

**Teach:** The first job of an AI assistant is to make the *next human action obvious*. Not send 300 creepy automated messages.

## 0:08–0:18 · Build the one-page lead board

Open [demo CSV](data/demo-leads.csv) and [START HERE](START-HERE.md).
- Import to a new Airtable base on desktop.
- Show **Name, Stage, Notes, Next Follow-Up, Consent to Contact**.
- Explain in plain language: "This is the scoreboard. No fancy CRM migration."
- Take 1 minute for attendees to locate lead **L-001**.

**Checkpoint:** Everyone can find L-001, or has a CSV fallback.

## 0:18–0:27 · Give AI a business brain

Show [BUSINESS-BRAIN.md](BUSINESS-BRAIN.md).
- Fill in only 4 facts live: business name, actual services, actual pricing rule, service area or UNKNOWN.
- Teach the difference between **verified** and **sounds plausible**.
- Paste [Prompt 1](PROMPTS.md#prompt-1-set-up-your-assistant) into ChatGPT.
- Show the assistant identifying what it needs before confidently quoting.

**Checkpoint:** Each attendee has one business-specific instruction and one hard boundary for their AI.

## 0:27–0:40 · The money moment: Find → Draft

- Use [Prompt 2](PROMPTS.md#prompt-2-find-todays-best-opportunities) to find up to 3 actionable leads.
- **Important:** If the connector isn't available, upload the *fictional* CSV or paste demo rows. Never fake a connected demo.
- Show why L-001 needs a reply, why a quoted lead may need a follow-up, and why Unknown/No consent blocks outbound messages.
- Use [Prompt 3](PROMPTS.md#prompt-3-draft-the-message). Read a natural draft aloud.
- Ask the room to critique it: "Would you actually send this to a neighbor?"

**Checkpoint:** We have an actually useful **draft**, not a message accidentally sent.

## 0:40–0:51 · Close the loop, no magic buttons

- Propose the next follow-up date and stage.
- Use [Prompt 4](PROMPTS.md#prompt-4-approve-one-specific-board-change) to show the old/new values before any write.
- On a *working authorized connector*, approve a **single** change to the fictional record and refresh Airtable to verify.
- On manual path, edit exactly one Airtable/spreadsheet row. This counts as success.
- Emphasize: "We did not build a lead-collecting webhook today. We built the operating habit that a future webhook can feed."

**Checkpoint:** One record has an accurate next action and date, verified on the board.

## 0:51–1:00 · Graduate and assign a 24-hour mission

Show [Prompt 5](PROMPTS.md#prompt-5-give-me-a-5-minute-daily-briefing).

**Audience challenge:**
1. Put 3 real *consented* leads in your private tracker, or keep practicing with fiction.
2. Identify one safe follow-up.
3. Draft one message and **review it** before sending through the normal business channel.
4. Record the next action and date.

Ask for one takeaway: "What's the first task you're taking away from yourself?"

**Finish:** "We didn't replace your CRM. We made the work impossible to ignore."

## Optional 1:00–1:30 · Office hours

Split attendees:
- **No connector:** Help them use CSV/Google Sheets.
- **Connected Airtable:** Verify safe record reads, then one approved practice update.
- **Advanced:** Sketch future contact capture and consent checks. No claims of a live Facebook → ChatGPT integration.

## Instructor preflight, before 4 PM

- [ ] Open the public workshop folder on a phone without signing in.
- [ ] Open demo CSV and verify 5 fictional rows / field names.
- [ ] Prepare a *separate demo Airtable base*, never your production CRM.
- [ ] In ChatGPT, run Prompt 1 from clean chat.
- [ ] Verify whether the Airtable plugin is actually available, and test **read first**.
- [ ] Test Prompt 2 with connector; also test the manual CSV fallback.
- [ ] Verify a single approved record update, or use manual update on screen.
- [ ] Put one QR code/short URL to the workshop folder on screen.
- [ ] Never promise LeadBridge or live unattended automation.

**If anything breaks:** Do the manual CSV version and continue. "Watch the working part; copy what matters" is much more professional than fumbling through OAuth live.
