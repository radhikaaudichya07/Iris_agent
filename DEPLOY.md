# Deploying Iris (always-on, for the judging window)

Iris uses **Socket Mode**, so it needs **no public URL or domain** — just a host that keeps
`python app.py` running 24/7. The repo is already committed and deploy-ready.

Recommended host: **Render** (clearest UI). Two options — free (with a keep-awake pinger) or
a small paid worker (zero hassle). Both are below.

---

## STEP 1 — Push the code to GitHub (one time)

1. Go to **https://github.com/new**
   - Repository name: `iris-slack-agent`
   - **Private** is fine. **Do NOT** add a README/.gitignore (the repo already has them).
   - Click **Create repository**.
2. GitHub shows a URL like `https://github.com/YOURNAME/iris-slack-agent.git`. Copy it.
3. In PowerShell, from the `iris` folder, run (replace the URL):
   ```powershell
   cd "C:\Users\Radhika Audichya\Documents\slack-ai\iris"
   git remote add origin https://github.com/YOURNAME/iris-slack-agent.git
   git branch -M main
   git push -u origin main
   ```
4. A browser window pops up to **sign in to GitHub** (Git Credential Manager) — approve it. The push completes.
   - ✅ Your `.env` is git-ignored, so your tokens are NOT uploaded. Good.

---

## STEP 2 — Deploy on Render

Go to **https://render.com** → sign up (GitHub login is easiest) → **New +**.

### Option A — Free (Web Service + keep-awake)  ·  $0
1. **New + → Web Service** → connect your `iris-slack-agent` repo → **Connect**.
2. Fill in:
   - **Language:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
   - **Instance Type:** **Free**
3. **Environment → Add Environment Variable** (three of them — copy from your `.env`):
   | Key | Value |
   |---|---|
   | `SLACK_BOT_TOKEN` | `xoxb-…` |
   | `SLACK_APP_TOKEN` | `xapp-…` |
   | `GROQ_API_KEY` | `gsk_…` |
4. **Create Web Service.** Watch the logs — you want to see `Bolt app is running!`.
5. Render gives you a URL like `https://iris-slack-agent.onrender.com`.
6. **Keep it awake** (free instances sleep after 15 min idle): go to **https://uptimerobot.com**,
   create a free **HTTP(s) monitor** pointing at that Render URL, interval **5 minutes**. This pings the
   health endpoint so the process never sleeps → Iris stays online for judging.

### Option B — Paid Background Worker  ·  ~$7/mo (no pinger, most reliable)
1. **New + → Background Worker** → connect the repo.
2. Build: `pip install -r requirements.txt` · Start: `python app.py`
3. Add the same three env vars.
4. **Create.** It runs continuously with no sleep and no pinger needed. Cancel after judging.

> For an $8k-prize submission judged over 3 weeks, Option B removes all risk. Option A is genuinely
> fine if you set up the UptimeRobot pinger.

---

## STEP 3 — Verify it's live
- In Render logs you should see `Assistant agent surface registered` then `Bolt app is running!`.
- In Slack, post an image in a channel where `@iria` is invited → Iris replies. It now works even
  with your laptop **off**.

---

## Redeploying after code changes
```powershell
git add -A
git commit -m "update"
git push
```
Render auto-redeploys on push.

---

## Notes
- **Preferences/history** live in SQLite on the host's disk. On Render's free/worker tiers the disk is
  ephemeral, so a redeploy resets them — fine for the demo. For durable storage, attach a Render **Disk**
  (paid) mounted where `iris_memory.db` lives.
- **Data policy:** enable **Zero Data Retention** in the Groq console → Data Controls (see `../iris.md`
  → Data & Privacy).
- **Other hosts:** Railway (`railway up`, deploys the folder directly) and Fly.io (`flyctl deploy`) also
  work — same Start Command and env vars.
