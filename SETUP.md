# Iris — Complete Setup Guide (from absolute scratch)

This is the everything-you-do-at-your-end guide. Follow it top to bottom, in order.
Don't skip steps. Each box is one small action. Tick them off as you go.

You will end with Iris running on your computer and replying to images in Slack.

**You need 4 things by the end:**
1. `SLACK_BOT_TOKEN` (starts `xoxb-`)
2. `SLACK_APP_TOKEN` (starts `xapp-`)
3. `GEMINI_API_KEY` (free)
4. Python installed

---

## PART 1 — Install the tools on your computer (one time)

### Step 1.1 — Install Python
- [ ] Go to **https://www.python.org/downloads/**
- [ ] Click the big yellow **Download Python 3.x** button.
- [ ] Run the downloaded file.
- [ ] ⚠️ **IMPORTANT:** on the first screen, tick the box **"Add python.exe to PATH"** (bottom of the window) BEFORE clicking Install.
- [ ] Click **Install Now**, wait, then **Close**.

### Step 1.2 — Check Python works
- [ ] Open **PowerShell** (press the Windows key, type `PowerShell`, hit Enter).
- [ ] Type this and press Enter:
  ```powershell
  python --version
  ```
- [ ] You should see something like `Python 3.12.4`. If you see an error, Python didn't install to PATH — reinstall and make sure you tick that box.

---

## PART 2 — Get your free Gemini key (the AI that reads images)

### Step 2.1
- [ ] Go to **https://aistudio.google.com/apikey**
- [ ] Sign in with any **Google account** (no credit card needed).
- [ ] Click **"Create API key"**.
- [ ] Click **"Create API key in new project"** if it asks.
- [ ] **Copy the key** it shows you (a long string). Paste it into a temporary notepad — you'll need it later. This is your `GEMINI_API_KEY`.

---

## PART 3 — Create your Slack workspace (where Iris lives)

The "no items in the dropdown" problem happens because you have no workspace yet. Fix that here.

### Step 3.1 — Create a free Slack workspace
- [ ] Go to **https://slack.com/get-started#/createnew**
- [ ] Enter your email → Slack sends you a **6-digit code** → check your email → enter the code.
- [ ] When asked **"What's the name of your company or team?"** → type anything, e.g. `Iris Dev`.
- [ ] When asked **"What's your team working on right now?"** → type anything, e.g. `Testing`.
- [ ] It may ask to add teammates → click **"Skip this step"**.
- [ ] You now have a workspace open in your browser. 🎉 Leave this tab open.

### Step 3.2 — (Recommended for the hackathon) Join the Slack Developer Program
> The hackathon wants you to demo in a **developer sandbox**. The free workspace above is enough to BUILD and TEST today. Do this step when you're ready to submit.
- [ ] Go to **https://api.slack.com/developer-program** → click **Join**.
- [ ] Provision a **sandbox** (a workspace you own). You can build in the free workspace now and move to the sandbox later if needed.

---

## PART 4 — Create the Slack app

### Step 4.1 — Start a new app
- [ ] Go to **https://api.slack.com/apps**
- [ ] Click **"Create New App"** → choose **"From scratch"**.
- [ ] **App Name:** type `Iris`
- [ ] **Pick a workspace:** the workspace you made in Step 3.1 should now appear in the dropdown. Select it.
- [ ] Click **"Create App"**.

You're now on your app's settings page. The left sidebar is where everything happens.

### Step 4.2 — Turn on Socket Mode (lets the app run from your laptop, no website needed)
- [ ] Left sidebar → **Socket Mode**.
- [ ] Toggle **"Enable Socket Mode"** to ON.
- [ ] A popup asks to create an **App-Level Token**. Give it a name like `socket` → click **Generate**.
- [ ] It shows a token starting with **`xapp-`**. **Copy it** to your notepad. This is your `SLACK_APP_TOKEN`.
- [ ] Click **Done**.

### Step 4.3 — Add Bot permissions (scopes)
- [ ] Left sidebar → **OAuth & Permissions**.
- [ ] Scroll to **"Scopes"** → **"Bot Token Scopes"** → click **"Add an OAuth Scope"** and add each of these (one at a time):
  ```
  files:read
  channels:history
  groups:history
  im:history
  im:read
  chat:write
  app_mentions:read
  users:read
  channels:read
  ```

### Step 4.4 — Subscribe to events (so Iris hears when an image is posted)
- [ ] Left sidebar → **Event Subscriptions**.
- [ ] Toggle **"Enable Events"** to ON.
- [ ] Expand **"Subscribe to bot events"** → click **"Add Bot User Event"** and add each:
  ```
  file_shared
  message.channels
  message.im
  app_mention
  ```
- [ ] Click **"Save Changes"** (bottom right). If it nags about reinstalling, that's fine — you'll install next.

### Step 4.5 — Install the app & get the bot token
- [ ] Left sidebar → **OAuth & Permissions** (or **Install App**).
- [ ] Click **"Install to Workspace"** → **"Allow"**.
- [ ] Back on the page, copy the **"Bot User OAuth Token"** (starts **`xoxb-`**) to your notepad. This is your `SLACK_BOT_TOKEN`.

### Step 4.6 — Turn on messaging tab (so you can DM Iris later)
- [ ] Left sidebar → **App Home**.
- [ ] Scroll to **"Show Tabs"** → tick **"Allow users to send Slash commands and messages from the messages tab"**.

---

## PART 5 — Put your keys into the project

You now have all 3 tokens in your notepad. Let's give them to the app.

### Step 5.1 — Open the project folder in PowerShell
- [ ] In PowerShell, paste this and press Enter:
  ```powershell
  cd "C:\Users\Radhika Audichya\Documents\slack-ai\iris"
  ```

### Step 5.2 — Create your .env file from the template
- [ ] Paste and Enter:
  ```powershell
  Copy-Item .env.sample .env
  ```
- [ ] Open the new `.env` file to edit it:
  ```powershell
  notepad .env
  ```
- [ ] Replace the placeholder text after each `=` with your real values (no quotes, no spaces):
  ```
  SLACK_BOT_TOKEN=xoxb-...paste yours...
  SLACK_APP_TOKEN=xapp-...paste yours...
  GEMINI_API_KEY=...paste yours...
  ```
- [ ] Save (Ctrl+S) and close Notepad.

---

## PART 6 — Install and run Iris

### Step 6.1 — Create a clean Python environment (one time)
- [ ] In PowerShell (still in the `iris` folder), paste and Enter:
  ```powershell
  python -m venv .venv
  ```
- [ ] Activate it:
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- [ ] ⚠️ If you get a red error about "running scripts is disabled", paste this ONCE, press Enter, type `Y`, then re-run the activate line above:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  ```
- [ ] When it works, your prompt line will start with **`(.venv)`**.

### Step 6.2 — Install the libraries (one time)
- [ ] Paste and Enter:
  ```powershell
  pip install -r requirements.txt
  ```
- [ ] Wait for it to finish (downloads a few packages).

### Step 6.3 — Start Iris
- [ ] Paste and Enter:
  ```powershell
  python app.py
  ```
- [ ] You should see log lines and a message that it connected (Socket Mode). **Leave this window open** — this is Iris running. To stop it later, press `Ctrl+C`.

---

## PART 7 — Test it in Slack

### Step 7.1 — Invite Iris into a channel
- [ ] Open your Slack workspace (browser or app).
- [ ] Go to any channel (e.g. `#general`), or create a channel called `#iris-test`.
- [ ] In the message box type **`/invite @Iris`** and send. (This step is REQUIRED — without it, image downloads fail.)

### Step 7.2 — Milestone A test (basic description)
- [ ] Drag any **image or screenshot** into the channel and send it.
- [ ] Within a few seconds, Iris replies **in a thread** describing the image (and reading any chart/text in it). ✅

### Step 7.3 — Milestone B test (the hero — context)
- [ ] In a thread, first type a question like: **"are we on track for the APAC target?"**
- [ ] Then, as a reply in that same thread, post a chart image.
- [ ] Iris replies **answering the question** using the chart, not just captioning it. ✅

---

## If something breaks — quick fixes

| What you see | Fix |
|---|---|
| `python not recognized` | Python isn't on PATH. Reinstall (Part 1) and tick "Add python.exe to PATH". |
| `running scripts is disabled` | Run the `Set-ExecutionPolicy` line in Step 6.1. |
| App starts but nothing happens when you post an image | Did you `/invite @Iris` into that channel? (Step 7.1) |
| Error mentioning `403` / `not_allowed` when downloading | Bot isn't in the channel, or a scope is missing — recheck Steps 4.3 and 7.1, then reinstall (4.5). |
| `KeyError: 'SLACK_BOT_TOKEN'` | Your `.env` isn't filled in or has typos. Recheck Part 5. |
| `missing_scope` | Add the missing scope in Step 4.3, then **reinstall** the app (Step 4.5). |
| Gemini rate-limit / quota error | Free tier is a few requests/minute. Wait a minute and retry; don't post many images at once. |

---

## What you should have at the end
- ✅ A PowerShell window running `python app.py` (Iris is live).
- ✅ Iris replying to images in your Slack channel with rich descriptions.
- ✅ Iris answering thread questions using posted charts.

When this works, tell me — next is **Milestone C: memory + image diffs** (the "whoa" moment).

**Every day you run Iris later, you only need:**
```powershell
cd "C:\Users\Radhika Audichya\Documents\slack-ai\iris"
.venv\Scripts\Activate.ps1
python app.py
```
(Parts 1–5 are one-time setup; you never repeat them.)
