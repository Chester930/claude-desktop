"""Pool of persistent ClaudeSDKClient connections, keyed by session key.

Replaces "spawn a new `claude` subprocess every turn + --resume" with one
long-lived subprocess per key, reused across turns via query()/receive_response().
Idle connections are evicted after a timeout so memory doesn't grow unbounded.
"""
import asyncio
import time

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

DEFAULT_IDLE_TIMEOUT = 30 * 60  # 30 minutes


class SessionPool:
    def __init__(self, idle_timeout: float = DEFAULT_IDLE_TIMEOUT):
        self._clients: dict[str, ClaudeSDKClient] = {}
        self._touched: dict[str, float] = {}
        self._idle_timeout = idle_timeout
        self._lock = asyncio.Lock()

    async def get_or_create(self, key: str, options: ClaudeAgentOptions) -> ClaudeSDKClient:
        async with self._lock:
            client = self._clients.get(key)
            if client is None:
                client = ClaudeSDKClient(options=options)
                await client.connect()
                self._clients[key] = client
            self._touched[key] = time.time()
            return client

    def has(self, key: str) -> bool:
        return key in self._clients

    async def evict(self, key: str) -> None:
        client = self._clients.pop(key, None)
        self._touched.pop(key, None)
        if client is not None:
            try:
                await client.disconnect()
            except Exception:
                pass

    async def prune_idle(self) -> int:
        now = time.time()
        stale = [k for k, t in self._touched.items() if now - t > self._idle_timeout]
        for k in stale:
            await self.evict(k)
        return len(stale)

    async def evict_all(self) -> None:
        for k in list(self._clients.keys()):
            await self.evict(k)

    def __len__(self) -> int:
        return len(self._clients)


async def run_idle_pruner(pool: SessionPool, interval: float = 300.0) -> None:
    """Background task: periodically evict connections idle past the timeout."""
    while True:
        await asyncio.sleep(interval)
        try:
            await pool.prune_idle()
        except Exception:
            pass
