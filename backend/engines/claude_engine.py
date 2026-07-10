"""
engines/claude_engine.py — Claude Code CLI 的 AgentEngine 實作。

這是 routes/teams.py::_agent_run_capture() 原本內嵌的 subprocess 組裝 +
`stream-json` 解析邏輯的忠實搬遷（2026-07-10 team 協作健檢那幾輪修過、
用真實 CLI 驗證過的行為，原封不動）：

- `--output-format stream-json --verbose`：逐行 JSON 事件輸出。
- `--permission-mode acceptEdits`（預設）：headless `-p` 模式下 stdin 沒有
  互動核准通道（已用真實 CLI 驗證：即使 stdin=PIPE，遇到需要核准的操作也
  只會在 3 秒後自動判斷，不會等待輸入），acceptEdits 讓 Write/Bash 這類
  操作可以正常執行，且 Claude Code 自身對敏感路徑（如 .claude/）的硬性
  保護不受影響、依然生效。
- 文字內容來自 `{"type":"assistant","message":{"content":[{"type":"text",...}]}}`
  或 `{"type":"text","text":...}` 事件；session id 來自
  `{"type":"result","session_id":...}`。
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from helpers import safe_kill_process, wrap_cmd

from .base import RunResult

name = "claude"

DEFAULT_PERMISSION_MODE = "acceptEdits"
VALID_PERMISSION_MODES = frozenset({
    "acceptEdits", "auto", "bypassPermissions", "manual", "dontAsk", "plan",
})


def _claude_bin() -> str:
    for mod_name in ("main", "backend.main", "__main__"):
        mod = sys.modules.get(mod_name)
        if mod and hasattr(mod, "CLAUDE_BIN"):
            return getattr(mod, "CLAUDE_BIN", "claude")
    return "claude"


async def run_turn(
    *,
    prompt: str,
    cwd: str,
    model: str,
    permission_mode: str,
    resume_session_id: "str | None",
    api_key: str,
    on_text,
    on_process=None,
    is_cancelled=None,
) -> RunResult:
    claude_bin = _claude_bin()
    cmd = [claude_bin, "-p", prompt, "--output-format", "stream-json", "--verbose"]
    if model and model not in ("sonnet", ""):
        cmd += ["--model", model]

    mode = permission_mode if permission_mode in VALID_PERMISSION_MODES else DEFAULT_PERMISSION_MODE
    cmd += ["--permission-mode", mode]

    if resume_session_id:
        cmd += ["--resume", resume_session_id]

    env = {**os.environ}
    if api_key:
        env["ANTHROPIC_API_KEY"] = api_key

    safe_cwd = cwd if (cwd and Path(cwd).is_dir()) else str(Path.home())
    output_parts: list[str] = []
    session_id = ""
    proc = None
    try:
        cmd = wrap_cmd(cmd[0], cmd[1:])
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            stdin=asyncio.subprocess.DEVNULL,
            cwd=safe_cwd,
            env=env,
        )
        if on_process:
            on_process(proc)

        async for line in proc.stdout:
            if is_cancelled and is_cancelled():
                safe_kill_process(proc)
                break

            raw = line.decode("utf-8", errors="replace").strip()
            if not raw:
                continue
            try:
                ev = json.loads(raw)
                chunk = ""
                if ev.get("type") == "assistant":
                    for block in ev.get("message", {}).get("content", []):
                        if isinstance(block, dict) and block.get("type") == "text":
                            chunk += block["text"]
                elif ev.get("type") == "text":
                    chunk = ev.get("text", "")
                elif ev.get("type") == "result" and ev.get("session_id"):
                    session_id = ev["session_id"]
                if chunk:
                    output_parts.append(chunk)
                    await on_text(chunk)
            except json.JSONDecodeError:
                pass
        await proc.wait()
    except Exception as e:
        return RunResult(output="".join(output_parts), session_id=session_id, error=str(e))

    return RunResult(output="".join(output_parts), session_id=session_id)
