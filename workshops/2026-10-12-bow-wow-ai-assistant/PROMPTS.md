# Copy/paste ChatGPT prompts

Use the prompts **one at a time**. Replace information in [BRACKETS]. Do not paste real customer details into public chats or the repository. For class, use fictional demo leads.

## Prompt 1: Set up your assistant

~~~text
Act as my careful front-office assistant for a pet waste removal business.

My verified business rules:
[PASTE COMPLETED BUSINESS-BRAIN.md CONTENT HERE]

Your first job is helping me organize leads and prepare follow-ups, NOT sending messages or taking payments.

Rules:
- Never guess prices, ZIP coverage, service availability, customer answers, or consent.
- Label unknown information UNKNOWN.
- Never send external messages, schedule outreach, or edit records without my explicit approval.
- Before a proposed CRM/Airtable change, show: lead ID, field, current value, proposed value, reason.
- Report only actions that were actually confirmed by a connected tool as completed.
- Keep customer-facing language warm, plain, and brief.

First, summarize the rules in 5 bullets, then identify any missing facts that would make a quote unsafe. Don't ask me to set up APIs or automation.
~~~

## Prompt 2: Find today's best opportunities

~~~text
Today is October 12, 2026 for this classroom exercise.
Review the fictional Leads table in My AI Lead Desk if my Airtable connector can access it. If you cannot access it, tell me and ask me to attach or paste data/demo-leads.csv; do not pretend you read it.

Show at most THREE leads that deserve attention today, ranked by:
1. An unanswered inbound request I have permission to respond to.
2. A previously quoted prospect due for a permitted follow-up.
3. A request blocked by missing details.

For each: lead ID, what we KNOW from the record, what's MISSING, one next action, and a reasonable follow-up date proposal. Flag Unknown/No consent for manual verification only. No outreach and no edits yet.
~~~

## Prompt 3: Draft the message

~~~text
Use the fictional lead with ID L-001 and the verified business rules.
Draft ONE helpful reply of at most 85 words.
It should feel like a real local service owner, not a marketing funnel.
Acknowledge the request, ask the single most useful missing question, and make the next step obvious.
No invented price, availability, discounts, ZIP coverage, or promises.
Show the draft, the contact-permission status from the record, and one suggested follow-up date.
DO NOT SEND IT.
~~~

## Prompt 4: Approve one specific board change

~~~text
For fictional lead L-001, propose the smallest Airtable update that matches the next action we just agreed to.
Before doing anything, display a table with the exact existing field values and proposed new values.
If you cannot read the real record, say so.
WAIT for my explicit approval before updating. Do not send any message.
After approval, use only the authorized connected action. If the action fails or is unavailable, show me what to edit manually, and do not claim it succeeded.
~~~

## Prompt 5: Give me a 5-minute daily briefing

~~~text
Read the current Leads table only if the connector provides actual current data. Otherwise tell me which file to upload.
Make a short morning scoreboard:
- New inbound leads that have not been answered
- Follow-ups due today
- Waiting on customer information
- Leads that should NOT be contacted (no/unknown consent, paused, opted out, closed)
- The 3 highest-value human actions to take next

Cite each recommendation with lead ID and source field. Do not infer missing lead history or report a message sent unless verified.
~~~

## Prompt 6: Turn what I learned into a repeatable procedure

~~~text
Help me write a one-page, beginner-friendly checklist for handling every new quote request.
Only use the business facts and steps we verified today.
Separate manual steps, ChatGPT-assisted drafting, and future automations.
Make it executable by a new employee and specify which actions require owner approval.
Do not introduce tools I haven't connected.
~~~

### How to use these safely

- Treat the AI as a **junior assistant with a checklist**, not a replacement for the actual CRM.
- You stay in control of quotes, booking, billing, outbound messages, and changes.
- A ChatGPT reply is not proof that Airtable was updated. Open the record and verify.
- The demo date is **October 12, 2026**. When using this after class, tell ChatGPT to use today's actual date, not the classroom date.
