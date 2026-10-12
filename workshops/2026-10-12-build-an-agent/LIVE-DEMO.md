# Instructor live demo: Real Airtable read → decision → approved write

A private **ScoopOS Bow Wow — AI Agent Demo (Fictional)** Airtable base was created in the host's connected account. It contains five fictional leads (L-001 through L-005) and a **Leads** table.

**Verified on Oct 11, 2026:** Reading five records via the connected Airtable plugin worked. One record update was written, read back and confirmed, then the demo data was restored to its original stage and follow-up date.

This verifies the **Airtable connector's basic read/write capability**, NOT that the ChatGPT Work agent or LeadBridge is configured or fully tested. The following demo is the real agent acceptance test.

## Recommended Work prompt

Copy into a **new Work conversation with Airtable actually connected**:

~~~text
Today we are demonstrating a supervised lead follow-up assistant.

Use the connected Airtable account and locate the base named "ScoopOS Bow Wow — AI Agent Demo (Fictional)", table "Leads". Work only with the five fictional rows. If that base is not available to you, STOP and report the connection/permission blocker.

1. Read all five records using the connected Airtable tool. Show each lead's exact Lead ID, Stage, Consent and Next Action.
2. Recommend the top lead to help next. Explain why and cite the actual record or record ID. Respect No and Unknown contact permission.
3. Draft a short, helpful customer response, but do not invent pricing, availability or route coverage and DO NOT SEND.
4. Propose an update for L-001 to Stage "Needs Reply", Follow Up "2026-10-13", and Next Action "Draft response prepared; await owner approval". Show the current field values beside the proposed new values.
5. STOP and ask for my explicit approval BEFORE any write. After my approval and a confirmed tool write, read the row again and report the actual new values. If the write isn't supported, tell me and provide manual steps.

Never say a message was sent, a quote was accepted, or a record was updated unless the connected tool confirms that event.
~~~

**Demo progression:** First do steps 1–4, pause for explicit approval, then authorize only that specific fictional write. Finally reopen the actual Airtable row and verify new values. Reset L-001 to Stage **New**, Follow Up **2026-10-12** and its original Next Action after class, not during the demonstration.

## What the student should see

- Actual records, not hallucinated lead names
- Permission-aware lead selection
- A real draft that hasn't been sent
- An exact before/after update proposal
- A separate approval step
- A confirmed CRM update only if tool access permits

## Student adaptation

Attendees **do not get access to the instructor's Airtable account**. They should copy [demo-leads.csv](demo-leads.csv) into their own private Airtable base (or use an existing private tracker with permission) and change the base name in the prompt.

## Important boundaries

- The host Airtable base is private and contains exclusively fictional examples.
- LeadBridge, Facebook lead imports, Quo, Sweep & Go and live external messaging are NOT part of this verified demo.
- Sending real follow-ups or making billing changes is out of scope.
