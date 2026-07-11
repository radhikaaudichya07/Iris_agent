"""
Iris — Slack Assistant/agent surface (Slack AI capabilities).

This makes Iris a first-class Slack *agent*: it lives in the AI side-panel
container, shows a thinking status, offers suggested prompts, and answers in a
proper agent thread. It's how a user configures Iris and asks it things —
distinct from the ambient, event-driven image describer in app.py.

Registered from app.py inside a try/except so that if the installed Bolt version
or the app's config doesn't support the Assistant class, the core still runs.
"""

from slack_bolt import Assistant


def register_assistant(app, memory, groq, parse_preferences, impact_line=None):
    assistant = Assistant()

    @assistant.thread_started
    def on_start(say, set_suggested_prompts):
        say(
            ":eye: *Hi, I'm Iris.* I describe every image posted in your channels for blind and "
            "low-vision teammates — reading the data in charts, answering the conversation around "
            "them, and remembering recurring dashboards to report only what changed.\n\n"
            "Tell me how you'd like descriptions, ask how I work, or ask for the accessibility report."
        )
        set_suggested_prompts(prompts=[
            {"title": "I use a screen reader — DM me", "message": "I use a screen reader, please DM me descriptions"},
            {"title": "Show the accessibility report", "message": "show me the accessibility report"},
            {"title": "Keep descriptions short", "message": "keep descriptions short"},
            {"title": "How do you work?", "message": "how do you work?"},
        ])

    @assistant.user_message
    def on_message(payload, set_status, say, context):
        set_status("is thinking…")
        text = (payload.get("text") or "").strip()
        user_id = context.get("user_id") or payload.get("user")

        low = text.lower()
        if any(w in low for w in ("report", "impact", "how many", "stats", "accessible so far")):
            if impact_line:
                say(":earth_africa: *Accessibility report*\n" + impact_line())
            else:
                stats = memory.get_stats()
                say(f":earth_africa: Iris has made *{stats.get('images_described', 0)}* images accessible so far.")
            return

        if "how do you work" in low or "what do you do" in low or low in ("help", "?"):
            say(
                "*How I work:*\n"
                "1. Someone posts an image in a channel I'm in.\n"
                "2. I read it — including the *data* inside charts and screenshots.\n"
                "3. I describe it as an *answer to the conversation* around it, and post that as text "
                "your screen reader can speak aloud.\n"
                "4. If it's a recurring dashboard, I report only what *changed*.\n"
                "5. Opt in below and I'll DM you each description in *your* preferred style."
            )
            return

        # Otherwise treat the message as a preference instruction.
        patch = parse_preferences(text)
        if patch:
            merged = memory.set_user_prefs(user_id, patch)
            extra = " I'll DM you a personalized description of every image from now on." \
                if merged.get("screen_reader") else ""
            say(f":white_check_mark: Got it — updated your settings.{extra}\n`{merged}`")
        else:
            say(
                "Tell me how you'd like images described — for example *“keep it short”*, "
                "*“always exact numbers”*, *“skip GIFs”*, *“explain acronyms”*, or "
                "*“I use a screen reader”* to get personal DMs."
            )

    app.assistant(assistant)
