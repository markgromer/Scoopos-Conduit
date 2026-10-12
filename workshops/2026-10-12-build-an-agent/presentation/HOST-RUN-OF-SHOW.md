# ScoopOS Bow Wow — 26:35 Masterclass Host Script

**Monday, October 12, 2026 · 4:00 PM America/Phoenix**  
**Workshop:** Build Your First AI Employee  
**Audience:** Local service-business owners, including complete AI beginners

## Open these tabs before Zoom

1. **Dedicated audience window, share ONLY this URL:** https://scoopos-bowwow-masterclass.markgromer.workers.dev/?audience=1
2. **Presenter notes console:** https://scoopos-bowwow-masterclass.markgromer.workers.dev/?presenter=1
3. **Student Agent Lab:** https://scoopos-agent-lab.markgromer.workers.dev/
4. **Private instructor Airtable demo:** Open the private base named `ScoopOS Bow Wow — AI Agent Demo (Fictional)` in your Airtable account.
5. **Live demo checklist:** https://github.com/markgromer/Scoopos-Conduit/blob/main/workshops/2026-10-12-build-an-agent/LIVE-DEMO.md
6. **Member handout:** https://scoopos-bowwow-masterclass.markgromer.workers.dev/?handout=1

> **Do not confuse what has been tested:** Cloudflare deck and Agent Lab are published. The Airtable connector's basic read/write was tested independently and the records were reset. The end-to-end Work agent test has not yet been demonstrated in the class. LeadBridge is not live.

## Timed sequence (26:35)

| # | Start | End | Pace | Scene |
|---|---:|---:|---:|---|
| 1 | 0:00 | 0:45 | 0:45 | OPEN / THE PROMISE |
| 2 | 0:45 | 2:00 | 1:15 | 01 / THE PROBLEM |
| 3 | 2:00 | 3:10 | 1:10 | 02 / THE SHIFT |
| 4 | 3:10 | 4:40 | 1:30 | 03 / THE ANATOMY |
| 5 | 4:40 | 5:55 | 1:15 | 04 / CHOOSE THE JOB |
| 6 | 5:55 | 7:30 | 1:35 | 05 / THE REAL WORKFLOW |
| 7 | 7:30 | 8:50 | 1:20 | 06 / BUSINESS TRUTH |
| 8 | 8:50 | 10:10 | 1:20 | 07 / CONNECT TO REALITY |
| 9 | 10:10 | 11:25 | 1:15 | 08 / CONTROL |
| 10 | 11:25 | 12:45 | 1:20 | 09 / PROOF |
| 11 | 12:45 | 13:45 | 1:00 | 10 / PICK THE RUNTIME |
| 12 | 13:45 | 17:00 | 3:15 | LIVE BUILD / PART 1 |
| 13 | 17:00 | 20:15 | 3:15 | LIVE BUILD / PART 2 |
| 14 | 20:15 | 23:05 | 2:50 | LIVE BUILD / PART 3 |
| 15 | 23:05 | 25:15 | 2:10 | THE LAST CHECK / ACCEPTANCE |
| 16 | 25:15 | 26:35 | 1:20 | FINISH / 24-HOUR MISSION |

## What to say and what to do

### Slide 01 · Stop prompting. Start delegating.

**Section:** OPEN / THE PROMISE · **Target pace:** 0:45

Welcome everyone. We have one objective: stop collecting clever prompts and build a worker that does one useful thing for your business.

By the end you'll have a role, verified knowledge, a workflow, rules for what it can touch, and a real test. I am not going to tell you that copying some text secretly creates a self-running employee.

**Ask the room:** Opening question: What's one repetitive thing you wish somebody else handled?

### Slide 02 · The lead didn't disappear. Your process did.

**Section:** 01 / THE PROBLEM · **Target pace:** 1:15

Use a fictional person named Jamie. Jamie messaged on Saturday about weekly cleanup. The owner saw it between jobs, got interrupted, and now no one knows whether a reply was sent.

This is not a marketing problem. It's a work-management problem. The AI agent should read the actual record, figure out what's missing, recommend a response, and make sure the owner has a next action.

**Ask the room:** Ask the room: Where does a customer go after they ask for a quote and don't book immediately?

### Slide 03 · Chatbots make words.Agents move work.

**Section:** 02 / THE SHIFT · **Target pace:** 1:10

A chatbot can respond based on what you type. An agent is designed to use tools and follow a repeatable process. The most important word is designed. You have to give it tools, permission boundaries, and a concrete job.

A ChatGPT Project can make an excellent reusable instruction workspace, but a Project alone does not create background automation. We will keep that distinction clear.

**Ask the room:** Ask: Can the AI prove it looked at the actual customer record, or did it only write a plausible paragraph?

### Slide 04 · A useful agent has six parts.

**Section:** 03 / THE ANATOMY · **Target pace:** 1:30

Walk through these like job onboarding. The job is the title on the door. Knowledge is the binder. Tools are the keys. Workflow is the standard procedure. Boundaries are the permissions. Proof is the supervisor checking the result.

If one is missing, the system can sound impressive while accomplishing very little.

**Ask the room:** Ask: Which one have most people been skipping? Usually tools, boundaries, or proof.

### Slide 05 · Don't hire AI torun the company.

**Section:** 04 / CHOOSE THE JOB · **Target pace:** 1:15

Don't start with 'manage my business.' It's too vague to test and too broad to trust. Ask members which job they would actually delegate this week.

Click a job tile on this slide and discuss the desired outcome. Then say that for the shared demo we'll use lead follow-up because everyone understands the cost of an ignored inquiry.

**Ask the room:** Audience participation: Which agent would you hire first? Click the most popular choice.

### Slide 06 · Watch the Lead Desk work.

**Section:** 05 / THE REAL WORKFLOW · **Target pace:** 1:35

This is the workflow we will build. Walk it from left to right. Note that 'read' means actual connected source data, not recollection. 'Verify' means pricing and route coverage can be unknown. 'Approve' means outbound messages and record changes wait for a human. 'Confirm' is a second read of the changed record.

LeadBridge is not finished and is not part of this class. We don't need it to teach real tool use.

**Ask the room:** Ask: At which step would you want the agent to stop and ask you? Show the approval gate.

### Slide 07 · Unknown is better than confidently wrong.

**Section:** 06 / BUSINESS TRUTH · **Target pace:** 1:20

This is a real record in our demo base, but the person is fictional. We know the dog count and ZIP, but we have no verified service-area coverage or current rate in this example.

Reveal the safe response. A good agent never pretends confidence equals correctness. It asks for what it needs, then moves the task forward.

**Ask the room:** Pause before revealing: What is the one fact we cannot responsibly promise?

### Slide 08 · Instructions aren't connections.

**Section:** 07 / CONNECT TO REALITY · **Target pace:** 1:20

When someone ticks Airtable in our builder, it does not magically create credentials. They must connect the right app inside their own account and check what operations it supports.

Our fictional Airtable base has been read, written, verified, and reset using connected tools. That's enough to stage the lesson, not proof that every member has the same permissions. Explain that Gmail/Drive are alternatives for other roles.

**Ask the room:** Ask: What's the difference between writing 'check email' and giving the agent permission to read the actual mailbox?

### Slide 09 · An agent needs boundaries.

**Section:** 08 / CONTROL · **Target pace:** 1:15

Ask who here would hand their business bank login to an employee on day one and say 'do whatever seems reasonable.' Exactly.

The agent's role and the connected app's permissions should match. Some things it can draft. Consequential actions require human review. In the developer sample, even proposing a record update does not save it. A separate approval button does.

**Ask the room:** Ask: Which kinds of actions would you NEVER allow without asking first?

### Slide 10 · Three tests. No magic tricks.

**Section:** 09 / PROOF · **Target pace:** 1:20

Tell members the completion screen isn't the success condition. We need evidence. Test 1: source ID matches actual record. Test 2: no invented quote. Test 3: no unapproved write or send.

A lesson with checkmarks and no connected data is still a design exercise. That's okay, but call it what it is.

**Ask the room:** Ask members: Would you trust an employee who simply said 'Done' but couldn't show which customer they contacted?

### Slide 11 · Where does the agent live?

**Section:** 10 / PICK THE RUNTIME · **Target pace:** 1:00

Participants have different plans and technical comfort levels. Everyone can develop a useful reusable instruction setup. Not everyone can run Work or create Workspace Agents. The optional API starter has real tool calls but needs Node.js and an API account.

For today's class use one available connected source and keep the task supervised. They don't need a full background system tonight.

**Ask the room:** Ask who can already see Work or has Airtable/Gmail connected. If not, use the Project/manual-input path.

### Slide 12 · Let's build your agent.

**Section:** LIVE BUILD / PART 1 · **Target pace:** 3:15

This is the hands-on moment. Ask members to open the Agent Lab on their own phone or a second browser tab. Show it on your shared screen.

Walk through Job and Business Brain. Demonstrate Lead Follow-Up, but let each member select a role. Type real business facts, and say UNKNOWN where facts aren't supplied. Give a clear pricing approval rule. The page generates instructions; it is not connected to ChatGPT yet.

Give participants about two minutes to fill this section. If they're stuck, they can use the instructor's sample business, but don't put actual customer data into a public site.

**Ask the room:** Checkpoint: Everybody should be able to say, 'My agent's job is ___, and it knows ___.'

### Slide 13 · Now give it a process.

**Section:** LIVE BUILD / PART 2 · **Target pace:** 3:15

Move to Workflow, Tools, and Guardrails in the builder. The default Lead Desk process gives six clear steps. Everyone should be able to edit that process to match their business without trying to invent API endpoints.

Pick one real source such as Airtable or Gmail. Explain that ticking the checkbox does not connect the app. In the final stage they will have to do that in their own ChatGPT account.

Keep all approval and evidence rules turned on. Every attendee should finish with an action sequence they can explain.

**Ask the room:** Checkpoint: Which source will the agent read first, and which action requires owner approval?

### Slide 14 · Install. Read. Prove it.

**Section:** LIVE BUILD / PART 3 · **Target pace:** 2:50

Have members choose the correct installation path. Show how to paste their generated AGENT.md instructions into a new ChatGPT Project. If you have Work, use the separate live-demo instructions and the connected fictional Airtable base.

Ask a real source-read question. Show the exact Lead ID and the fields the agent retrieved. If there is no connector, a clearly labeled private uploaded sample is an acceptable manual first exercise, but it's not a proof of connected access.

Do not attempt to build a Facebook lead webhook during this class.

**Ask the room:** Checkpoint: Can you prove the agent read an actual authorized source, or is it truthfully blocked?

### Slide 15 · Don't trust it until it passes.

**Section:** THE LAST CHECK / ACCEPTANCE · **Target pace:** 2:10

Show three tests quickly. For a live demonstration: read L-001, ask it for an unverified price (must say unknown), then ask it to message Jamie and mark Won (must not do either without approval).

If Work can make an authorized edit, show the proposed field changes, approve the specific fictional change, then independently read back the row. This write is optional for students; the important requirement is an honest pass or blocker.

Members check their tests in Agent Lab only after running them in their own accounts. The website does not verify their external actions.

**Ask the room:** Ask one attendee to report: Which of the three tests passed, and which was blocked?

### Slide 16 · Your agent's first paid job is tomorrow.

**Section:** FINISH / 24-HOUR MISSION · **Target pace:** 1:20

Close with a simple 24-hour mission. Ask everyone to give their agent one real task and share the result in ScoopOS without exposing customer information. The result can be a successful read and good draft, or a useful blocked result showing what connection is missing.

Remind them the code starter is an optional advanced track. They don't need to become software developers to get value. Give both links and the member handout.

**Ask the room:** Final question: What is your agent's first job tomorrow?

## How to keep the class on time

The live build (slides 12–14) has a combined 9 minutes, 20 seconds. If you fall behind, demo the input and the copy/installation step yourself and tell attendees they can complete remaining fields after class. Do not spend five minutes troubleshooting any one student's OAuth.

Open **?audience=1** in its own browser **window**. That window contains slides ONLY and is the **sole window you select in Zoom's Share → Window menu**. Put `?presenter=1` in another window on a second monitor or outside the shared application. **Never share the whole screen/monitor while the private presenter notes are visible.** The private view displays a yellow warning. Advance slides from the presenter view; the audience view follows automatically. Click **Start timer** at the opening. Press **→** or **Space** for the next scene; press **R** for the resource panel.

## Live demo checklist

- [ ] Open fictional Airtable base and verify L-001 has stage `New`, follow-up `2026-10-12`.
- [ ] Use ChatGPT with an authorized Airtable connection to read the exact record, not remembered details.
- [ ] Ask it to identify missing facts. It must not invent service availability, price or area.
- [ ] Request a short message draft, with no send action.
- [ ] Request a proposed stage/follow-up edit. Require the exact old/new values and owner approval.
- [ ] If you authorize the demo edit, verify the actual changed row in Airtable before claiming success.
- [ ] Restore the fictional demo base afterward using the instructor's documented initial values.
- [ ] Never show a real customer's private information during screen share.

## Troubleshooting

**No Work access?** Use a ChatGPT Project and a private sample file. This establishes a reusable assistant workflow but does not prove autonomous execution.

**Airtable unavailable?** Use an authorized Gmail read or the fictional CSV. Be explicit that a CSV exercise is not connected live data.

**Member only has a phone?** They can complete the Agent Lab on mobile and copy the generated instructions. They can install the Project and connect the app later from desktop if necessary.

**Presentation breaks?** The GitHub repository contains the source and all talking points; follow this run-of-show and open the student lab directly.

**People ask for Facebook lead automation?** It is a later lesson. LeadBridge and Meta webhooks are not deployed by this workshop.

## Share after class

- Slides: https://scoopos-bowwow-masterclass.markgromer.workers.dev/
- Agent builder: https://scoopos-agent-lab.markgromer.workers.dev/
- Handout: https://scoopos-bowwow-masterclass.markgromer.workers.dev/?handout=1
- GitHub workshop: https://github.com/markgromer/Scoopos-Conduit/tree/main/workshops/2026-10-12-build-an-agent

Encourage members to share one real supervised agent action and one limitation discovered. Keep customer data out of public posts.
