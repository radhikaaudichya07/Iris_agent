# Iris — dev setup (Milestone A + B)

Lean Bolt-Python Socket Mode app. Describes images posted in Slack for blind teammates,
using the surrounding thread as context. See `../iris-build-plan.md` for the full sprint.

## 1. Create the Slack app
Slack Developer Program → provision a **sandbox** → create an app.

**Socket Mode:** turn ON. Generate an **App-Level Token** with scope `connections:write` → `SLACK_APP_TOKEN`.

**Bot Token Scopes** (OAuth & Permissions):
```
files:read        channels:history   groups:history
im:history        im:read            im:write          chat:write
app_mentions:read users:read         channels:read     search:read.public
assistant:write
```
- `im:write` — so Iris can DM personalized descriptions to opted-in screen-reader users.
- `search:read.public` — enables the Real-Time Search API (`assistant.search.context`) for related
  cross-channel context. (Private-channel search would need a user token `xoxp-` with `search:read.private`.)
- `assistant:write` — the Slack Assistant/agent surface.

**Event Subscriptions** (subscribe to bot events):
```
file_shared       message.channels   message.im       app_mention
assistant_thread_started             assistant_thread_context_changed
```

**Agent / Assistant** (left sidebar → *Agents & AI Apps*, or *App Home*): enable the **Assistant**
so Iris appears in the AI side-panel with suggested prompts. If your workspace/app version doesn't
offer it, the core image-describer still runs (the Assistant is registered defensively).

Install to the workspace → copy the **Bot User OAuth Token** → `SLACK_BOT_TOKEN`.

**Gemini API key** (free, no payment): https://aistudio.google.com/apikey → `GEMINI_API_KEY`.

## 2. Run
```bash
python -m venv .venv && . .venv/Scripts/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.sample .env        # then edit .env
python app.py
```

## 3. Test
1. **Invite the bot to a channel** (`/invite @iris`) — required or file downloads 403.
2. Post an image → Iris replies in-thread with a data-rich description (Milestone A).
3. Ask a question in a thread, then post a relevant chart in that thread → Iris answers the
   question, not just captions the image (Milestone B — the hero).

## Notes
- **Real-Time Search API** = method `assistant.search.context` (params `query`, `channel_types`).
  Swap it into `fetch_thread_context()` to pull *related* history across channels, not just this thread.
- **`slack create agent`** (Claude Agent SDK + Bolt Python template) is the recommended base when
  you add the **MCP memory server** (Milestone C/D) — it already ships the Claude agent + tool loop.
- Loop guard: the handler ignores non-images and the bot's own uploads.
