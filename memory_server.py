"""
Iris Memory — a small MCP server (Milestone C).
Exposes 4 tools over the Model Context Protocol, backed by SQLite:

  - get_user_prefs(user_id)                      -> prefs JSON
  - set_user_prefs(user_id, prefs_json)          -> merged prefs JSON
  - get_image_history(image_key)                 -> last structured summary ('' if unseen)
  - save_image_snapshot(image_key, summary)      -> 'ok'

This is a real, standalone MCP server: you can also connect it to Claude Desktop
or the MCP Inspector as evidence of MCP integration. Iris (app.py) connects to it
as an MCP client via memory_client.py.

Run standalone (stdio):  python memory_server.py
"""

import os
import json
import sqlite3

from mcp.server.fastmcp import FastMCP

DB = os.path.join(os.path.dirname(__file__), "iris_memory.db")
mcp = FastMCP("iris-memory")


def _db() -> sqlite3.Connection:
    con = sqlite3.connect(DB)
    con.execute(
        "CREATE TABLE IF NOT EXISTS user_prefs("
        "user_id TEXT PRIMARY KEY, prefs TEXT, updated_at TEXT)"
    )
    con.execute(
        "CREATE TABLE IF NOT EXISTS image_history("
        "image_key TEXT PRIMARY KEY, structured_summary TEXT, last_seen TEXT)"
    )
    con.execute(
        "CREATE TABLE IF NOT EXISTS stats(name TEXT PRIMARY KEY, value INTEGER)"
    )
    return con


@mcp.tool()
def bump_stat(name: str, by: int = 1) -> str:
    """Increment a named counter (e.g. 'images_described') and return the new total."""
    con = _db()
    con.execute(
        "INSERT INTO stats(name, value) VALUES(?, ?) "
        "ON CONFLICT(name) DO UPDATE SET value = value + ?",
        (name, by, by),
    )
    con.commit()
    row = con.execute("SELECT value FROM stats WHERE name=?", (name,)).fetchone()
    con.close()
    return str(row[0] if row else 0)


@mcp.tool()
def get_stats() -> str:
    """Return all impact counters as a JSON object."""
    con = _db()
    rows = con.execute("SELECT name, value FROM stats").fetchall()
    con.close()
    return json.dumps({n: v for n, v in rows})


@mcp.tool()
def get_user_prefs(user_id: str) -> str:
    """Return the stored preferences JSON for a user (or '{}' if none)."""
    con = _db()
    row = con.execute("SELECT prefs FROM user_prefs WHERE user_id=?", (user_id,)).fetchone()
    con.close()
    return row[0] if row else "{}"


@mcp.tool()
def set_user_prefs(user_id: str, prefs_json: str) -> str:
    """Merge the given preferences JSON into a user's stored preferences. Returns merged JSON."""
    con = _db()
    row = con.execute("SELECT prefs FROM user_prefs WHERE user_id=?", (user_id,)).fetchone()
    merged = json.loads(row[0]) if row else {}
    merged.update(json.loads(prefs_json))
    con.execute(
        "INSERT OR REPLACE INTO user_prefs(user_id, prefs, updated_at) "
        "VALUES(?, ?, datetime('now'))",
        (user_id, json.dumps(merged)),
    )
    con.commit()
    con.close()
    return json.dumps(merged)


@mcp.tool()
def list_sr_users() -> str:
    """Return a JSON list of user_ids who have opted in as screen-reader users
    (prefs contain "screen_reader": true) — they get personalized DMs."""
    con = _db()
    rows = con.execute("SELECT user_id, prefs FROM user_prefs").fetchall()
    con.close()
    out = []
    for uid, prefs in rows:
        try:
            if json.loads(prefs).get("screen_reader"):
                out.append(uid)
        except Exception:
            pass
    return json.dumps(out)


@mcp.tool()
def get_image_history(image_key: str) -> str:
    """Return the last structured summary for a recurring image (or '' if unseen)."""
    con = _db()
    row = con.execute(
        "SELECT structured_summary FROM image_history WHERE image_key=?", (image_key,)
    ).fetchone()
    con.close()
    return row[0] if row else ""


@mcp.tool()
def save_image_snapshot(image_key: str, structured_summary: str) -> str:
    """Save the latest structured summary for a recurring image (for future diffs)."""
    con = _db()
    con.execute(
        "INSERT OR REPLACE INTO image_history(image_key, structured_summary, last_seen) "
        "VALUES(?, ?, datetime('now'))",
        (image_key, structured_summary),
    )
    con.commit()
    con.close()
    return "ok"


if __name__ == "__main__":
    mcp.run()  # stdio transport
