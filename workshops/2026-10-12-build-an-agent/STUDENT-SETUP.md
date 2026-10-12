# Student guide: install a usable business agent

## Begin
Open **https://scoopos-agent-lab.markgromer.workers.dev/**. Answer the six building questions. Download AGENT.md and its three live tests.

### Route A: ChatGPT Project (broadest access)
1. In ChatGPT sidebar, create **New project**.
2. Name it after the agent.
3. From the project's menu choose **Project settings** and paste **AGENT.md** as project instructions.
4. Privately add verified SOPs, price lists, FAQs or other allowed files; do not publish customer lists in GitHub.
5. Start a conversation inside the project and give it a narrow task.
6. This is a reusable **AI-assisted workspace**, NOT a background bot or automatic app-triggered agent.

### Route B: Work with connected apps (eligible plans)
1. Create the Project or begin a Work session with your full AGENT.md instructions.
2. In Settings → Plugins, connect the one actual app you want the agent to read (Airtable, Gmail, Drive, etc., where supported).
3. Verify the correct linked account and permissions. Don't assume an app has write access or all records.
4. In Work, have the agent read ONE record and cite the exact item. If it can't, fix connection/permissions or use a manual sample.
5. Ask for a draft and verify it has **not** sent a message.
6. Only then approve a small, safe external change if the tool supports it. Re-read the record to confirm.
7. If you want a scheduled task, configure it separately in Scheduled/Work where eligible. Project files are not necessarily available to that future scheduled execution, so put important instructions in the task itself.

### Route C: Workspace Agent (Business, Enterprise, Edu, permissions required)
Create the agent under the workspace Agents feature. Paste AGENT.md, attach knowledge, configure its plugins and allowed actions, then test and publish if permitted. Workspace admin controls may restrict creation and connected apps.

### Route D: Independent API runtime (developer)
See [agent-starter/README.md](agent-starter/README.md). It uses actual model tool calls and a local demo lead database. It requires an OpenAI API key and separate API billing. This is NOT a shared public API key, and the sample server is only designed for localhost.

## Understand what the steps mean
- **Agent spec:** What it should do.
- **Knowledge:** Facts and policies it can cite.
- **Tools:** What it is authorized and technically able to read/change.
- **Runtime:** ChatGPT Project, Work, Workspace Agent, or your own app.
- **Trigger:** Manual task, schedule, or event configured outside the written prompt.
- **Evaluation:** Proof the agent read the real item, didn't invent facts, and respected approvals.

**The finished product is the installed and TESTED agent, not the downloaded spec.**

Official feature references:
- https://help.openai.com/en/articles/10169521-projects-in-chatgpt
- https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex
- https://help.openai.com/en/articles/20001143-chatgpt-workspace-agents-for-enterprise-and-business
- https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt
