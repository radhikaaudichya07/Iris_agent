# Iris — Demo Video: Script + How to Record

Target **2:35**, hard cap **3:00**. Judging is async — **this video IS your pitch.** Judges may watch
muted, so **burn in captions.** An accessibility project with an inaccessible video looks bad, so captions
are both good practice and points.

---

## THE OPENING NARRATION (say this, or use as on-screen captions verbatim)

> "1 in 6 people live with a disability, and the EU Accessibility Act is now enforceable — yet every chart,
> dashboard, and screenshot posted in Slack is invisible to blind teammates, because alt-text is optional
> and nobody adds it. **Iris** is a Slack agent that reads every image, answers the conversation around it,
> remembers recurring dashboards, and writes native screen-reader alt-text — automatically. It turns
> accessibility from the disabled employee's daily burden into something the platform just does, and proves
> it with a live compliance metric. Built on Slack's MCP, Real-Time Search, and Assistant APIs."

Use this as the spine: the **first ~25 seconds** are this hook over the landing page; the **middle** is the
live Slack demo; the **end** returns to the landing page's closing line + architecture.

---

## SHOT LIST — alternating LANDING PAGE ⟷ LIVE SLACK

Open two windows before recording:
- **Browser** at your live site: `https://iris-agent-8msr.onrender.com/` (landing) and `/architecture`.
- **Slack** (`IRIA` workspace) with `#product-metrics`, `@iria` invited, two chart images ready.

| Time | SHOW (screen) | SAY / caption |
|---|---|---|
| 0:00–0:08 | **Landing hero** (scroll slowly over the headline + Slack mock) | "Every chart posted in Slack is invisible to a blind teammate." |
| 0:08–0:25 | **Landing "before/after" section** | The pitch hook (first 2 sentences above). Let the "Image. No description." card sit on screen. |
| 0:25–0:55 | **LIVE Slack**: type a question in a thread, post the APAC chart | "Watch. Someone asks if APAC is on track, then drops a chart." → Iris replies **answering the question**, and the reply carries **native alt-text**. |
| 0:55–1:20 | **LIVE Slack**: re-post the updated dashboard | "Same dashboard tomorrow — Iris reports only what changed." Show the "🔁 Change since last time" reply. |
| 1:20–1:45 | **LIVE Slack**: DM Iris "keep it short" → post an image | "Tell it how you read, and it remembers." Next description comes back as one line. |
| 1:45–2:05 | **LIVE Slack**: open **App Home** (the Impact panel) | "And it proves its impact — images made accessible, hours saved." Point at the live number. Then caption: **"EU Accessibility Act is now law. Iris makes your workspace compliant — automatically."** |
| 2:05–2:20 | **Landing /architecture** page | "Built on Slack's MCP, Real-Time Search, and Assistant APIs." |
| 2:20–2:35 | **Landing closing panel** ("Put every teammate in the conversation") | "Images are the wall. Text is the door. Iris opens it — for everyone." End card: **Iris — Slack Agent for Good.** |

**Most memorable 30 seconds = 0:00–0:25 hook + the 0:25–0:55 "it answered the question" reveal.** Nail those.

---

## HOW TO RECORD IT (step by step, Windows)

### 1. Pick a recorder (any one)
- **Easiest:** **Loom** (loom.com, free) — records screen + your voice, gives a link instantly.
- **Built-in, no install:** press **Win + Alt + R** (Xbox Game Bar) to record the screen. Voice: enable mic in Game Bar settings.
- **Best quality / free:** **OBS Studio** (obsproject.com) — screen capture + mic; export MP4.

Record at **1080p**, windowed so text is large and legible.

### 2. Stage the two windows
- Left/full: **browser** on the landing page.
- Have **Slack** ready to Alt-Tab to for the live parts.
- Do a dry run once so the Slack replies appear quickly (Groq takes ~2–4s — that's fine, don't cut it, it shows it's real).

### 3. Record in segments (don't do it in one nervous take)
- Segment A: scroll the **landing page** slowly (hero → before/after → closing). ~40s of footage.
- Segment B: the **live Slack demo** (question+chart, re-post diff, DM short, App Home number). ~90s.
- Segment C: the **architecture page**. ~15s.
- You'll stitch A→B→A/C in editing.

### 4. Add captions (required-ish for an a11y project)
- **Fastest:** upload the raw video to **YouTube (unlisted)** → YouTube auto-generates captions → fix typos in YouTube Studio. Judges watch it there.
- **Burned-in (looks best):** use **CapCut** (free) → "Auto captions" → it transcribes and overlays text → export MP4, then upload to YouTube/Vimeo public.

### 5. Voice or no voice
- **With voice:** read the narration column calmly. Best option.
- **No voice (fine):** add the narration as **on-screen captions** timed to each shot, plus soft royalty-free music (YouTube Audio Library only — no copyrighted tracks, per the rules).

### 6. Export & submit
- Under **3:00**, MP4, 1080p.
- Upload **public** to **YouTube / Vimeo** (the rules require a public link).
- Put the link on the Devpost submission form.

---

## Pre-flight checklist (do NOT skip)
- [ ] Bot is **live** (Render up) and `@iria` is invited to `#product-metrics`.
- [ ] Two chart images ready (one is an updated version for the "diff" beat).
- [ ] Reset your prefs first so the "keep it short" beat is a clean before/after.
- [ ] App Home Impact number shows a real count (post a few images first so it's not 0).
- [ ] Captions on. Under 3:00. No copyrighted music. English.
- [ ] Sandbox test access invited: `slackhack@salesforce.com`, `testing@devpost.com`.
- [ ] Backup: pre-record the Slack clips separately so a live glitch can't ruin the take.
