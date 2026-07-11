"""
Iris — Milestones A + B + C  (free Groq vision tier)
----------------------------------------------------
A) An image is posted -> download it -> Groq reads it (incl. chart data) -> threaded reply.
B) THE HERO: pull the surrounding thread and describe the image as an ANSWER to it.
C) THE WHOA: recall a recurring image via the MCP memory server and describe the DIFF.

Run: python app.py   (Socket Mode — no public URL needed)
Requires the scopes/events listed in README.md.
"""

import os
import json
import base64
import logging

import requests
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from groq import Groq

from memory_client import MemoryClient

load_dotenv()  # read tokens from the .env file

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("iris")

app = App(token=os.environ["SLACK_BOT_TOKEN"])
groq = Groq(api_key=os.environ["GROQ_API_KEY"])
memory = MemoryClient()   # MILESTONE C: MCP-backed image history + user prefs

VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"   # Groq free tier, vision-capable
IMAGE_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp"}


# --- helpers ---------------------------------------------------------------

def download_slack_file(url_private_download: str) -> bytes:
    """Slack private files require the BOT TOKEN as a Bearer header. The bot
    must also be a member of the channel or the download 403s."""
    resp = requests.get(
        url_private_download,
        headers={"Authorization": f"Bearer {os.environ['SLACK_BOT_TOKEN']}"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.content


def rts_related(client, query: str, action_token: str | None, limit: int = 5) -> str:
    """REAL-TIME SEARCH: pull *related* discussion from across the workspace via
    Slack's `assistant.search.context`. This is RTS used for its actual purpose —
    cross-channel context, not the immediate thread. Needs an action_token (which
    arrives on the message event) + the search:read.public scope. Falls back to ''."""
    if not action_token or not query.strip():
        return ""
    try:
        res = client.api_call("assistant.search.context", params={
            "query": query[:400],
            "action_token": action_token,
            "content_types": "messages",
            "limit": str(limit),
        })
        msgs = res.get("results", {}).get("messages", [])
        related = [m.get("content", "") for m in msgs if m.get("content")]
        if related:
            log.info("iris: RTS returned %d related messages", len(related))
        return "\n".join(related)
    except Exception as e:
        log.warning("RTS assistant.search.context unavailable (fallback): %s", e)
        return ""


def fetch_thread_context(client, channel: str, thread_ts: str, message_ts: str,
                         action_token: str | None = None, limit: int = 12) -> str:
    """MILESTONE B (hero): the conversation the image landed in.

    Immediate thread/history via the Conversations API (the right tool for that),
    PLUS cross-channel *related* context via the Real-Time Search API when an
    action_token is available. Both feed the description."""
    texts = []
    try:
        hist = client.conversations_history(channel=channel, limit=limit)
        for m in reversed(hist.get("messages", [])):  # oldest -> newest
            if m.get("ts") != message_ts and m.get("text"):
                texts.append(m["text"])
    except Exception as e:
        log.warning("history fetch failed: %s", e)

    if thread_ts and thread_ts != message_ts:
        try:
            rep = client.conversations_replies(channel=channel, ts=thread_ts, limit=50)
            for m in rep.get("messages", []):
                if m.get("ts") != message_ts and m.get("text"):
                    texts.append(m["text"])
        except Exception as e:
            log.warning("replies fetch failed: %s", e)

    seen, out = set(), []
    for t in texts:
        if t not in seen:
            seen.add(t)
            out.append(t)

    # Real-Time Search: related discussion elsewhere in the workspace.
    related = rts_related(client, " ".join(out[-3:]), action_token)
    if related:
        out.append("[Related discussion elsewhere in the workspace]\n" + related)
    return "\n".join(out)


def personalize_text(base_description: str, prefs: dict) -> str:
    """Reformat an already-generated description to one reader's preferences
    (text-only, no extra vision call). Used for personalized DMs to opted-in users."""
    style = prefs_to_style(prefs)
    if not style:
        return base_description
    resp = groq.chat.completions.create(
        model=VISION_MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": (
            "Rewrite the image description below to match this reader's preferences. "
            "Keep all factual content accurate; only change length/emphasis/formatting. "
            "Output ONLY the rewritten description — no preamble, no 'here is', no notes.\n"
            f"{style}\n\nDescription:\n{base_description}"
        )}],
    )
    return (resp.choices[0].message.content or base_description).strip()


def prefs_to_style(prefs: dict) -> str:
    """MILESTONE D: turn a stored preference profile into prompt instructions."""
    if not prefs:
        return ""
    lines = []
    if prefs.get("verbosity") == "short":
        lines.append("Be very brief: 1-2 sentences, only the single most important point.")
    elif prefs.get("verbosity") == "detailed":
        lines.append("Be thorough and include every data point you can read.")
    if prefs.get("numbers") == "exact":
        lines.append("Always give exact figures, never approximate.")
    elif prefs.get("numbers") == "rounded":
        lines.append("Round numbers for brevity.")
    if prefs.get("skip_decorative"):
        lines.append("If the image is purely decorative (meme/GIF/emoji reaction), say so in one short line and stop.")
    if prefs.get("explain_acronyms"):
        lines.append("Briefly expand any acronyms or jargon you see.")
    return ("\nThis reader has set preferences — follow them strictly:\n- "
            + "\n- ".join(lines) + "\n") if lines else ""


def describe_image(image_bytes: bytes, mimetype: str, thread_context: str,
                   prior_summary: str = "", prefs: dict | None = None) -> tuple[str, str]:
    """Returns (human_description, structured_summary).
    The structured_summary is a one-line snapshot we store for future diffs."""
    prompt = (
        "You are Iris, an accessibility agent. Describe this image for a blind teammate "
        "using a screen reader. If it is a chart, dashboard, or screenshot, READ THE ACTUAL "
        "DATA — figures, labels, axis values, error text — never just 'a chart'.\n"
        "Start with a ONE-SENTENCE headline of the most important thing, then supporting detail.\n"
        "CONFIDENCE: a blind reader cannot check your work, so never present a guess as fact. "
        "If the image is blurry, low-resolution, cropped, or you are unsure of any figure, BEGIN your "
        "reply with '⚠︎ Low confidence —' and say exactly what is unclear.\n"
    )
    prompt += prefs_to_style(prefs or {})
    if thread_context.strip():
        prompt += (
            "\nThis image was posted into the Slack conversation below. Describe the image as an "
            "ANSWER to what is being discussed — lead with the point that matters to this thread, "
            f"then the supporting detail:\n\n---\n{thread_context}\n---\n"
        )
    if prior_summary.strip():
        # MILESTONE C (the whoa): this recurring image was seen before -> describe the DIFF.
        prompt += (
            "\nYou have described this SAME recurring image before. Its previous snapshot was:\n"
            f"\"{prior_summary}\"\n"
            "Lead your description with what has CHANGED since then (e.g. 'Same dashboard as before, "
            "except ...'). If nothing material changed, say so in one line.\n"
        )
    prompt += (
        "\nAt the very END of your reply, on a new line, output 'SUMMARY:' followed by a single-line, "
        "data-focused snapshot of this image's key facts (for future comparison)."
    )

    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    resp = groq.chat.completions.create(
        model=VISION_MODEL,
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url",
                 "image_url": {"url": f"data:{mimetype};base64,{b64}"}},
            ],
        }],
    )
    text = (resp.choices[0].message.content or "").strip()
    if "SUMMARY:" in text:
        desc, _, summary = text.partition("SUMMARY:")
        return desc.strip(), summary.strip()
    return text, text[:300]


def parse_preferences(text: str) -> dict:
    """MILESTONE D: turn a plain-language DM into a structured preference patch."""
    resp = groq.chat.completions.create(
        model=VISION_MODEL,
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": (
                "A blind Slack user is telling you how they want images described. "
                "Extract their intent as a JSON object using ONLY these keys when relevant: "
                '"verbosity" ("short"|"standard"|"detailed"), "numbers" ("exact"|"rounded"), '
                '"skip_decorative" (true/false), "explain_acronyms" (true/false), '
                '"screen_reader" (true if they say they use a screen reader / are blind / want personal DMs). '
                "Output ONLY the JSON object, nothing else. If nothing matches, output {}.\n\n"
                f'User said: "{text}"'
            ),
        }],
    )
    raw = (resp.choices[0].message.content or "{}").strip()
    if "{" in raw:  # tolerate stray text around the JSON
        raw = raw[raw.index("{"): raw.rindex("}") + 1]
    try:
        return json.loads(raw)
    except Exception:
        return {}


# --- event handler ---------------------------------------------------------

@app.event("file_shared")
def _ignore_file_shared(event, logger):
    pass  # images are handled via the richer `message` event instead


@app.event("message")
def handle_message(event, client, logger):
    """Fires on channel/DM messages. Routes to: (1) describe an image, or
    (2) MILESTONE D — a plain-language preference DM."""
    if event.get("bot_id") or event.get("subtype") not in (None, "file_share"):
        return  # ignore bot messages, edits, joins, etc.

    user_id = event.get("user")
    images = [f for f in (event.get("files") or []) if f.get("mimetype") in IMAGE_TYPES]

    # (2) Preference DM: a text-only direct message to Iris.
    if not images and event.get("channel_type") == "im" and event.get("text", "").strip():
        patch = parse_preferences(event["text"])
        if patch:
            merged = memory.set_user_prefs(user_id, patch)
            client.chat_postMessage(channel=event["channel"],
                                    text=f":white_check_mark: Got it — I'll remember that. Your settings: `{json.dumps(merged)}`")
        else:
            client.chat_postMessage(channel=event["channel"],
                                    text="Tell me how you'd like images described — e.g. *\"keep it short\"*, "
                                         "*\"always exact numbers\"*, *\"skip GIFs\"*, or *\"explain acronyms\"*.")
        return

    if not images:
        return

    # (1) Describe an image. The channel reply is NEUTRAL (one message serves everyone);
    #     opted-in screen-reader users additionally get a description in THEIR own style by DM.
    channel = event["channel"]
    message_ts = event["ts"]
    thread_ts = event.get("thread_ts") or message_ts   # reply lands in-thread either way
    action_token = event.get("action_token")           # enables Real-Time Search when present
    context = fetch_thread_context(client, channel, thread_ts, message_ts, action_token)
    sr_users = [u for u in memory.list_sr_users() if u != user_id]
    log.info("iris: image msg channel=%s thread_ts=%s context_chars=%d sr_users=%d",
             channel, thread_ts, len(context), len(sr_users))

    for f in images:
        url = f.get("url_private_download") or f.get("url_private")
        image_bytes = download_slack_file(url)

        # MILESTONE C: recall prior snapshot of this recurring image, then store the new one.
        image_key = f"{channel}:{f.get('name') or f.get('id')}"
        prior_summary = memory.get_image_history(image_key)
        description, summary = describe_image(image_bytes, f["mimetype"], context, prior_summary)
        memory.save_image_snapshot(image_key, summary)

        if prior_summary.strip():
            tag = "🔁 *Change since last time* — "
        elif context.strip():
            tag = "↪︎ *Answering the conversation* — "
        else:
            tag = ""
        client.chat_postMessage(channel=channel, thread_ts=thread_ts,
                                text=f":eye: *Iris:* {tag}{description}")

        # Personalized delivery: DM each opted-in screen-reader user their own version.
        for uid in sr_users:
            try:
                variant = personalize_text(description, memory.get_user_prefs(uid))
                client.chat_postMessage(channel=uid,
                                        text=f":eye: *Iris* (image in <#{channel}>): {variant}")
            except Exception as e:
                log.warning("SR DM to %s failed: %s", uid, e)


# --- App Home: a Block Kit control panel (for sighted configuration) --------

def build_home(prefs: dict) -> dict:
    v = prefs.get("verbosity", "standard")
    nums = prefs.get("numbers", "standard")
    skip = bool(prefs.get("skip_decorative"))
    acro = bool(prefs.get("explain_acronyms"))
    sr = bool(prefs.get("screen_reader"))
    return {
        "type": "home",
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": "👁  Iris — image accessibility for Slack"}},
            {"type": "section", "text": {"type": "mrkdwn", "text":
                "I describe every image posted in your channels for blind and low-vision teammates — "
                "reading the *data* inside charts, *answering* the conversation around them, and "
                "*remembering* recurring dashboards so I report only what *changed*."}},
            {"type": "divider"},
            {"type": "section", "text": {"type": "mrkdwn", "text":
                f"*Personal delivery*\nScreen-reader DMs: *{'ON — I DM you a personalized description of every image' if sr else 'off'}*"}},
            {"type": "actions", "elements": [
                {"type": "button",
                 "text": {"type": "plain_text", "text": "Turn OFF personal DMs" if sr else "I use a screen reader — DM me"},
                 "action_id": "toggle_sr"},
            ]},
            {"type": "divider"},
            {"type": "section", "text": {"type": "mrkdwn", "text":
                f"*Your description style*\n"
                f"• Length: *{v}*\n• Numbers: *{nums}*\n"
                f"• Skip decorative images: *{'on' if skip else 'off'}*\n"
                f"• Explain acronyms: *{'on' if acro else 'off'}*"}},
            {"type": "actions", "elements": [
                {"type": "button", "text": {"type": "plain_text", "text": "Short"}, "action_id": "set_short"},
                {"type": "button", "text": {"type": "plain_text", "text": "Standard"}, "action_id": "set_standard"},
                {"type": "button", "text": {"type": "plain_text", "text": "Detailed"}, "action_id": "set_detailed"},
            ]},
            {"type": "actions", "elements": [
                {"type": "button", "text": {"type": "plain_text", "text": "Toggle exact numbers"}, "action_id": "toggle_numbers"},
                {"type": "button", "text": {"type": "plain_text", "text": "Toggle skip decorative"}, "action_id": "toggle_decorative"},
                {"type": "button", "text": {"type": "plain_text", "text": "Reset"}, "action_id": "reset_prefs", "style": "danger"},
            ]},
            {"type": "context", "elements": [{"type": "mrkdwn", "text":
                "💬 Tip: you can also just *DM me* in plain language — “keep it short”, “always exact numbers”, “skip GIFs”."}]},
        ],
    }


def _republish(client, user_id):
    client.views_publish(user_id=user_id, view=build_home(memory.get_user_prefs(user_id)))


@app.event("app_home_opened")
def show_home(event, client):
    _republish(client, event["user"])


@app.action("set_short")
def _set_short(ack, body, client):
    ack(); uid = body["user"]["id"]; memory.set_user_prefs(uid, {"verbosity": "short"}); _republish(client, uid)


@app.action("set_standard")
def _set_standard(ack, body, client):
    ack(); uid = body["user"]["id"]; memory.set_user_prefs(uid, {"verbosity": "standard"}); _republish(client, uid)


@app.action("set_detailed")
def _set_detailed(ack, body, client):
    ack(); uid = body["user"]["id"]; memory.set_user_prefs(uid, {"verbosity": "detailed"}); _republish(client, uid)


@app.action("toggle_numbers")
def _toggle_numbers(ack, body, client):
    ack(); uid = body["user"]["id"]
    cur = memory.get_user_prefs(uid).get("numbers")
    memory.set_user_prefs(uid, {"numbers": "standard" if cur == "exact" else "exact"})
    _republish(client, uid)


@app.action("toggle_decorative")
def _toggle_decorative(ack, body, client):
    ack(); uid = body["user"]["id"]
    cur = bool(memory.get_user_prefs(uid).get("skip_decorative"))
    memory.set_user_prefs(uid, {"skip_decorative": not cur})
    _republish(client, uid)


@app.action("reset_prefs")
def _reset_prefs(ack, body, client):
    ack(); uid = body["user"]["id"]
    memory.set_user_prefs(uid, {"verbosity": "standard", "numbers": "standard",
                                "skip_decorative": False, "explain_acronyms": False})
    _republish(client, uid)


@app.action("toggle_sr")
def _toggle_sr(ack, body, client):
    ack(); uid = body["user"]["id"]
    cur = bool(memory.get_user_prefs(uid).get("screen_reader"))
    memory.set_user_prefs(uid, {"screen_reader": not cur})
    _republish(client, uid)


# --- Slack Assistant/agent surface (Slack AI capabilities) ------------------
# Registered defensively: if the running Bolt version or app config doesn't
# support the Assistant class, the core image-describer still runs.
try:
    from assistant_agent import register_assistant
    register_assistant(app, memory, groq, parse_preferences)
    log.info("iris: Assistant agent surface registered")
except Exception as e:
    log.warning("iris: Assistant surface not registered (core still runs): %s", e)


def _start_health_server():
    """Serves the landing page at / and the architecture diagram at /architecture,
    on the same host that runs the Socket Mode agent. Any other path returns a 200
    health check (keeps free hosts awake). Socket Mode itself needs no inbound port."""
    port = int(os.environ.get("PORT", "0") or 0)
    if not port:
        return
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    here = os.path.dirname(os.path.abspath(__file__))

    def _read(name):
        try:
            with open(os.path.join(here, name), "rb") as fh:
                return fh.read()
        except Exception:
            return None

    class _H(BaseHTTPRequestHandler):
        def do_GET(self):
            path = self.path.split("?")[0].rstrip("/") or "/"
            body = None
            if path in ("/", "/index.html"):
                body = _read("landing.html")
            elif path.startswith("/architecture"):
                body = _read("architecture.html")
            if body is not None:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"Iris is running")

        def log_message(self, *a):
            pass

    threading.Thread(
        target=lambda: HTTPServer(("0.0.0.0", port), _H).serve_forever(),
        daemon=True,
    ).start()
    log.info("iris: web + health server listening on :%d", port)


if __name__ == "__main__":
    _start_health_server()
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
