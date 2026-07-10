# Iris — Demo Video Script (target 2:35, hard cap 3:00)

Judges are not required to watch past 3 minutes, and the "magic" must land in the first 30 seconds.
This script is shot-by-shot: **[SCREEN]** = what to show, **[VO]** = what you say (or caption).

> ♿ Meta-touch that scores points: **turn on captions/subtitles** for your own video (YouTube auto-captions
> are fine, or burn them in). An accessibility project with an inaccessible video reads badly. Also keep
> narration unhurried — clarity over speed.

---

## Pre-stage before recording (so it's smooth)

- A Slack channel `#product-metrics` with **@iris invited**, app running (`python app.py`).
- Two chart images ready on your desktop:
  - **chart-v1.png** — Q3 revenue: APAC $4.2M, EMEA $3.1M, Americas $2.8M (APAC highest).
  - **chart-v2.png** — same chart but APAC dropped to $3.0M (for the diff).
  - *(Generate both with any chart tool; label the bars with values so the model reads them.)*
- A second Slack user account (or your own DM) to show personalization.
- Open tabs ready: the **landing page** and the **architecture diagram** artifacts.
- Reset prefs in the App Home first, so the "learns you" beat starts clean.

---

## 0:00 – 0:22 · The hook (the problem)

**[SCREEN]** Open on the **landing page hero** (or a real Slack image with a screen reader voicing it).
**[VO]**
> "This is what a blind teammate hears when someone drops a chart in Slack…"
> *(let a screen reader say, or caption:)* **“Image. No description.”**
> "No data. No context. A decision gets made in that thread — based on a chart they were never able to read.
> Slack has alt-text, but it's optional, so nobody adds it. Meet **Iris**."

## 0:22 – 0:55 · Milestone A + B — it answers the conversation

**[SCREEN]** In `#product-metrics`, type and send: *"Are we on track for the APAC target of $3.5M?"*
Then post **chart-v1.png**.
**[VO]**
> "The moment an image is posted, Iris describes it — and not just 'a bar chart.' It reads the actual data.
> But here's the key move: it read the **question** in the thread first."

**[SCREEN]** Iris's threaded reply appears: *"↪︎ Answering the conversation — Yes, APAC is $4.2M, 20% over
the $3.5M target being discussed…"* Highlight the first line.
**[VO]**
> "It didn't caption the picture. It **answered the question** — the way a sighted colleague would."

## 0:55 – 1:25 · Milestone C — it remembers, and reports the diff

**[SCREEN]** Post **chart-v2.png** (same dashboard, APAC now $3.0M).
**[VO]**
> "Teams post the same dashboards every day. Watch what happens when I post an updated version."

**[SCREEN]** Iris replies: *"🔁 Change since last time — Same dashboard as before, except APAC dropped from
$4.2M to $3.0M…"*
**[VO]**
> "A **diff**, not a wall of text — powered by a memory server it talks to over MCP. That's genuinely more
> useful than what a sighted person gets glancing at the chart."

## 1:25 – 1:55 · Milestone D — it learns how *you* read

**[SCREEN]** Open a DM with Iris. Type: *"keep it short."* Iris replies: *"Got it — I'll remember that."*
**[SCREEN]** (Optional) Open the **App Home** tab — show the preference panel with buttons.
**[VO]**
> "Every person reads differently. Just tell Iris in plain language — and it remembers."

**[SCREEN]** Back in the channel, post **chart-v1.png** again. Iris's reply is now **one tight line**.
**[VO]**
> "Same image — but now, for me, one headline. It learned me. That's the difference between a caption bot
> and an accessibility product."

## 1:55 – 2:20 · How it's built (credibility)

**[SCREEN]** Cut to the **architecture diagram** artifact.
**[VO]**
> "Under the hood: a Slack Bolt agent fuses three signals — a vision model that reads the image, the thread
> around it via Real-Time Search, and an **MCP memory server** for history and preferences. All Slack-native."

## 2:20 – 2:35 · The impact close

**[SCREEN]** Landing page closing panel: *"Put every teammate in the conversation."*
**[VO]**
> "One in six people live with a disability. Iris shifts accessibility from the disabled employee's daily
> burden to something the workplace just provides — automatically, in context, for everyone. That's Iris."

**[SCREEN]** End card: **Iris · Slack Agent for Good** + the eye mark.

---

## Recording checklist
- [ ] Under 3:00 (aim 2:35). First 30s shows the problem + first "wow."
- [ ] Captions on (accessibility + judges may watch muted).
- [ ] Every claim is shown happening live, not just narrated.
- [ ] Screen text large enough to read at 720p.
- [ ] Public link on YouTube/Vimeo; no copyrighted music.
- [ ] Show the app actually running (the requirement: footage of the working project).
