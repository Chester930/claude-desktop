"""2026-07-11：handle_chat（主聊天室，選了某個 agent 之後打字聊天）之前
完全沒有讀取 agent 的 engine: frontmatter 欄位，寫死呼叫 Claude——就算把
某個 agent 設成 engine: codex，透過主聊天室互動時這個設定會被完全忽略。

這裡驗證：agent 宣告 engine: codex 時，handle_chat 真的會呼叫
codex_engine.run_turn()，完全不觸碰 SessionPool/ClaudeSDKClient 或
claude_engine；agent 宣告 engine: claude（或沒宣告）時，維持現有行為
100% 不變（走 legacy subprocess，因為測試環境沒有 HAS_AGENT_SDK）。
"""
import json

import pytest

from engines.base import RunResult

pytestmark = pytest.mark.asyncio


def _write_agent(agents_dir, agent_id: str, engine: str = "", skills: list = None) -> None:
    agents_dir.mkdir(parents=True, exist_ok=True)
    skills_yaml = f"skills: [{', '.join(skills)}]\n" if skills else ""
    engine_line = f"engine: {engine}\n" if engine else ""
    (agents_dir / f"{agent_id}.md").write_text(
        f"---\nname: {agent_id}\ndescription: test\n{skills_yaml}{engine_line}---\n\nagent body 內容\n",
        encoding="utf-8",
    )


async def _read_sse_events(resp) -> list:
    body = (await resp.content.read()).decode("utf-8")
    events = []
    for line in body.splitlines():
        if line.startswith("data: "):
            try:
                events.append(json.loads(line[len("data: "):]))
            except json.JSONDecodeError:
                pass
    return events


async def test_handle_chat_routes_to_codex_when_agent_declares_it(client, monkeypatch, app):
    import main
    _write_agent(main.AGENTS_DIR, "codex-chat-agent", engine="codex")

    captured = {}

    async def fake_codex_run_turn(**kwargs):
        captured["kwargs"] = kwargs
        await kwargs["on_text"]("Hello from codex")
        return RunResult(output="Hello from codex", session_id="sid-codex-chat")

    async def fake_claude_run_turn(**kwargs):
        raise AssertionError("claude_engine.run_turn should not be called for a codex-declared agent")

    from engines import codex_engine, claude_engine
    monkeypatch.setattr(codex_engine, "run_turn", fake_codex_run_turn)
    monkeypatch.setattr(claude_engine, "run_turn", fake_claude_run_turn)

    resp = await client.post("/api/chat", json={
        "message": "你是哪個引擎？", "client_id": "test-client-codex", "agent": "codex-chat-agent",
    })
    assert resp.status == 200
    events = await _read_sse_events(resp)

    assert "kwargs" in captured
    assert captured["kwargs"]["prompt"]  # full_message 有被組出來傳進去
    assistant_events = [e for e in events if e.get("type") == "assistant"]
    assert any("Hello from codex" in b.get("text", "") for e in assistant_events for b in e["message"]["content"])


async def test_handle_chat_still_uses_claude_when_no_engine_declared(client, monkeypatch, app):
    """沒有宣告 engine:（或宣告 claude）時，維持現有行為——這裡的測試環境
    沒有 Agent SDK（HAS_AGENT_SDK 應為 False 或 pool 不可用），所以會走
    legacy subprocess 路徑，跟這次改動之前完全一樣。"""
    import main
    _write_agent(main.AGENTS_DIR, "claude-chat-agent", engine="")

    codex_called = False

    async def fake_codex_run_turn(**kwargs):
        nonlocal codex_called
        codex_called = True
        return RunResult(output="should not happen")

    from engines import codex_engine
    monkeypatch.setattr(codex_engine, "run_turn", fake_codex_run_turn)

    async def fake_create_subprocess_exec(*args, **kwargs):
        class _FakeStdout:
            def __init__(self):
                self._lines = [b'{"type":"result","session_id":"sid-legacy"}\n']

            def __aiter__(self):
                return self

            async def __anext__(self):
                if not self._lines:
                    raise StopAsyncIteration
                return self._lines.pop(0)

        class _FakeProc:
            def __init__(self):
                self.stdout = _FakeStdout()
                self.returncode = 0

            async def wait(self):
                return 0

        return _FakeProc()

    monkeypatch.setattr(main.asyncio, "create_subprocess_exec", fake_create_subprocess_exec)

    resp = await client.post("/api/chat", json={
        "message": "hi", "client_id": "test-client-claude", "agent": "claude-chat-agent",
    })
    assert resp.status == 200
    await _read_sse_events(resp)

    assert not codex_called
