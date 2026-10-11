# Start here: 5-minute setup

You need: a web browser, ChatGPT, and optionally Airtable. You do **not** need GitHub, programming, a credit card, or an API key to complete the basic lesson.

## Step 1: Get the practice leads

Choose one:
- **Try the lesson first:** open [demo-leads.csv](data/demo-leads.csv), then click **Download raw file** (or use the browser's save command).
- **Start a real empty board:** download [blank-leads.csv](data/blank-leads.csv).

If GitHub's menus are confusing, use the repository's **Code → Download ZIP**, unzip it, and look in the data folder. All examples are fictional. Don't mix them into a real customer system.

## Step 2: Create the board

**Airtable path (recommended on a desktop browser):**
1. Go to [airtable.com](https://airtable.com) and create a new **blank base**. Name it **My AI Lead Desk**.
2. Click **+ Add or import**, choose **CSV file**, and upload the demo file.
3. Choose **Create a new table**, enable **Use first row as headers**, and finish importing.
4. Name the table **Leads**.
5. Check that names, stages, follow-up dates, and notes are in their proper columns.
6. Optionally change **Stage** and **Consent to Contact** to single-select fields, and **Next Follow-Up** to a date field. Keep all imported dates in YYYY-MM-DD format.

Airtable's native CSV import is available in the browser. The mobile app does not currently support this import. Airtable reference: https://support.airtable.com/articles/9412806945-importing-third-party-data-into-airtable

**Simplest fallback:** Open Google Sheets, import the CSV, and rename the sheet **Leads**. If you only have a phone and can't import comfortably, skip this step for now and paste the five fictional rows into ChatGPT during the demo.

## Step 3: Give AI the rules, not your passwords

Open [BUSINESS-BRAIN.md](BUSINESS-BRAIN.md). Fill in your real services, where you work, and what the assistant must **never guess**. Missing prices and schedule information are fine: mark them **UNKNOWN**.

Open ChatGPT. Copy [Prompt 1](PROMPTS.md#prompt-1-set-up-your-assistant) and fill the bracketed details. No customer records are needed yet.

## Step 4: Connect only if available

If your ChatGPT account offers the **Airtable plugin/connector**:
1. Open the ChatGPT plugin picker/settings.
2. Connect **your** Airtable account and authorize **your new demo base**, following the prompts.
3. Ask ChatGPT to **read the first five rows from My AI Lead Desk → Leads**. Verify the names match the CSV.
4. If a connection is unavailable or a permission is missing, **stop here** and use the manual CSV path. The lesson still works.

**Don't assume** "connected" means ChatGPT can automatically run unattended in the background. Also don't authorize edits to your production CRM for this beginner exercise.

## Step 5: Run one realistic example

Use [Prompt 2](PROMPTS.md#prompt-2-find-todays-best-opportunities), then [Prompt 3](PROMPTS.md#prompt-3-draft-the-message).

Your checkpoint:
- Identify the lead needing attention.
- Draft a reply that asks one useful question without inventing a price.
- Decide the follow-up date.
- Record the next action in your board, manually or after a specific approval.

You're done when you can point to **one lead, one next action, and one date**. That's a working business process, not a screenshot of software you may never touch again.
