"""
Synchronous bridge to the Iris memory MCP server.

The MCP Python SDK is async-only, but Slack Bolt handlers are sync. This wraps a
persistent MCP client session running on a background asyncio loop, and exposes
plain sync methods the app can call from inside an event handler.
"""

import os
import sys
import json
import asyncio
import threading

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MemoryClient:
    def __init__(self):
        self._loop = asyncio.new_event_loop()
        threading.Thread(target=self._loop.run_forever, daemon=True).start()
        self._session: ClientSession | None = None
        self._await(self._connect())

    # --- plumbing ---
    def _await(self, coro, timeout: int = 60):
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result(timeout=timeout)

    async def _connect(self):
        params = StdioServerParameters(
            command=sys.executable,
            args=[os.path.join(os.path.dirname(__file__), "memory_server.py")],
        )
        self._stdio_ctx = stdio_client(params)
        read, write = await self._stdio_ctx.__aenter__()
        self._session_ctx = ClientSession(read, write)
        self._session = await self._session_ctx.__aenter__()
        await self._session.initialize()

    async def _call(self, name: str, args: dict) -> str:
        res = await self._session.call_tool(name, args)
        return "".join(c.text for c in res.content if getattr(c, "type", None) == "text")

    def call(self, _tool: str, **args) -> str:
        return self._await(self._call(_tool, args))

    # --- convenience API ---
    def get_user_prefs(self, user_id: str) -> dict:
        return json.loads(self.call("get_user_prefs", user_id=user_id) or "{}")

    def set_user_prefs(self, user_id: str, patch: dict) -> dict:
        return json.loads(self.call("set_user_prefs", user_id=user_id, prefs_json=json.dumps(patch)))

    def list_sr_users(self) -> list:
        return json.loads(self.call("list_sr_users") or "[]")

    def bump_stat(self, name: str, by: int = 1) -> int:
        return int(self.call("bump_stat", name=name, by=by) or 0)

    def get_stats(self) -> dict:
        return json.loads(self.call("get_stats") or "{}")

    def get_image_history(self, image_key: str) -> str:
        return self.call("get_image_history", image_key=image_key)

    def save_image_snapshot(self, image_key: str, summary: str) -> None:
        self.call("save_image_snapshot", image_key=image_key, structured_summary=summary)
