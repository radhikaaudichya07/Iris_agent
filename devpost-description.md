## 💡 Inspiration

Slack runs on images — charts, dashboards, screenshots, diagrams get dropped into channels all day. But for a **blind or low‑vision teammate using a screen reader, every one of those images is a locked door.** The screen reader hits the image and says three words: *"Image. No description."* No data, no context. A decision gets made in that thread based on a chart they were never able to read.

Slack *does* support alt‑text — but it's optional and manual, so almost nobody adds it. The accessibility feature exists; the accessibility does not.

And this isn't only a moral problem anymore — it's a **legal and organizational** one. The **European Accessibility Act** became enforceable in June 2025, and the **ADA** and **Section 508** already require accessible workplace tools. Yet the burden today falls on the disabled employee to compensate — DM‑ing a colleague *"what's in that image?"* over and over.

We wanted to flip that: **make accessibility the platform's job, not the disabled person's daily burden.**

## 👁 What it does

**Iris is a Slack agent that makes every image accessible — automatically — and proves it.**

The moment an image is posted, Iris replies with a rich, screen‑reader‑ready description, and it goes far beyond captioning:

- **Reads the data** — not *"a bar chart,"* but the actual figures, labels, axis values, and error text inside it.
- **Answers the conversation** — it reads the surrounding thread and describes the image *as an answer to what's being discussed.* Ask *"are we hitting the APAC target?"*, drop a chart, and Iris replies *"Yes — APAC is $4.2M, 20% over target,"* not a neutral caption.
- **Remembers and diffs** — for recurring dashboards it reports only what changed: *"Same dashboard as yesterday, except APAC dropped from $4.2M to $3.0M — now below target."*
- **Learns how you read** — DM Iris *"keep it short"* or *"always exact numbers,"* and every future description respects it. Screen‑reader users can opt in to personalized descriptions delivered by DM.
- **Writes native alt‑text** — descriptions are attached as standards‑compliant screen‑reader alt‑text, not just chat prose.
- **Proves impact** — a live counter tracks images made accessible and manual alt‑texting time saved, viewable in the App Home and via the Assistant ("show me the accessibility report").

The result: a blind teammate finally participates as an equal, and the organization makes automated, measurable progress toward its accessibility obligations.

## 🛠 How we built it

Iris is built end‑to‑end on the Slack platform:

- **Slack Bolt (Python) + Socket Mode** — the agent core; no public endpoint needed.
- **Slack Assistant / Agent APIs** — Iris lives in the AI side‑panel with suggested prompts and a thinking status, so it's a first‑class *agent*, not a legacy bot.
- **MCP server (custom)** — a Model Context Protocol server, backed by SQLite, exposing tools for per‑user preferences, per‑image history (for diffs), and impact stats. The agent talks to it over the MCP protocol.
- **Real‑Time Search API** (`assistant.search.context`) — pulls related cross‑channel conversation for context, alongside the Conversations API for the immediate thread.
- **Block Kit** — the App Home control panel and preference toggles.
- **Vision** — a multimodal model (Llama‑4 via Groq) reads the image content; the description is delivered as clean text (best for screen readers) plus native alt‑text.
- **Deployment** — hosted 24/7 on Render so it runs without a laptop.

**Accessibility‑by‑design, in the product itself:** descriptions are plain text (optimal for screen readers, not decorative Block Kit), and all our materials use *Atkinson Hyperlegible* — a typeface engineered by the Braille Institute for low‑vision readability — with reduced‑motion‑safe animations.

## 🧗 Challenges we ran into

- **Getting the *conversation*, reliably.** Our first version listened to the `file_shared` event, whose thread data is unreliable — so in a thread Iris couldn't see the question. We switched to the `message` event (which carries `thread_ts` directly) and made context‑gathering robust by reading both the thread and recent channel history.
- **"Isn't this just an image captioner?"** Raw captioning is commodity. The real work was making it *not* a wrapper: reading thread context, remembering images to diff them, and building a per‑user model — things only possible inside Slack, with state.
- **Trust for an accessibility tool.** A blind user can't verify a description, so a confidently‑wrong reading is worse than none. We added a confidence hedge: low‑certainty reads are flagged, never presented as fact.
- **The reader‑vs‑poster problem.** A channel message is one‑to‑many, so "personalized per reader" doesn't work for a public post. We made channel replies neutral and deliver personalized descriptions to opted‑in screen‑reader users by DM.
- **Data governance.** Sending workplace images to a model is sensitive. We use inference‑only processing (no training), store no image bytes (only a one‑line summary + preferences), run with zero‑data‑retention, and kept the vision engine swappable for enterprise data‑residency.

## 🏆 Accomplishments we're proud of

- It **actually works and is deployed** — not a demo‑ware mockup.
- It uses **all three** hackathon technologies (Slack AI/Assistant, MCP, Real‑Time Search), each doing real work.
- It's a genuine accessibility product — coherent right down to an accessible marketing site and an accessibility typeface.
- It turns a niche‑sounding idea into an **organization‑wide, regulation‑relevant** tool with a measurable impact number.

## 📚 What we learned

- **Blind people read with their ears (or a Braille display).** Text is fully accessible to them via screen readers — images are the one thing that isn't. Iris is fundamentally a *translator from image to text.*
- **Context is the difference between captioning and comprehension.** The same image means different things depending on the question around it.
- Slack's agentic platform (MCP + RTS + Assistant APIs) is genuinely powerful for grounding an agent in real conversational data without hoarding it.

## 🚀 What's next

- **Native alt‑text at upload** and an admin **weekly accessibility‑coverage digest** to a channel.
- **On‑demand retrieval** ("Iris, read me every chart posted in #metrics this week").
- **Beyond images:** huddle captions, voice‑note transcription, and canvas accessibility — the same pattern applied across every visual/audio surface in Slack.

**Accessibility isn't a feature. It's the difference between being in the conversation and being shut out of it. Iris puts every teammate in the conversation.**
