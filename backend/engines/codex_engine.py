"""
engines/codex_engine.py — OpenAI Codex CLI 的 AgentEngine 實作。

⚠️ 尚未用真實 `codex` CLI 驗證過 ⚠️
這個環境沒有安裝 codex，以下實作是根據 OpenAI 官方文件寫的第一版（2026-07
查證，來源見下）。跟這次幫 Claude 那幾個引擎修 bug 的方法論不一樣——那些
都是先用真實 CLI 實測過（例如 acceptEdits 底下 Write/Bash 到底能不能跑）
才動手，這個檔案目前只是「照文件寫的最佳猜測」，行為沒有保證。

拿到有安裝 codex CLI 的機器後，跑 scripts/probe_codex_cli.py（跟這次
`claude` CLI 驗證用的 permtest/accepttest 手法一樣：直接呼叫、印出原始
事件、人工比對這個檔案的解析邏輯有沒有對上），把落差回報回來再校正。

參考文件（2026-07 查證）：
- https://developers.openai.com/codex/noninteractive （非互動模式 exec）
- https://developers.openai.com/codex/cli/reference （全域 flags）

已知（文件記載，未實測）：
- 非互動呼叫：`codex exec [--json] [--sandbox <mode>] [--cd <dir>]
  [--model <name>] "<prompt>"`。
- `--json` 輸出 JSON Lines，逐行一個事件。已知事件型別：
  `thread.started`（含 `thread_id`，UUID）、`turn.started`、
  `turn.completed`（含 `usage`）、`turn.failed`、`item.started` /
  `item.completed`（`item.type` 含 `agent_message`／`command_execution`／
  `reasoning`／檔案異動／MCP 工具呼叫；文字內容在 `item.completed` 且
  `item.type == "agent_message"` 時的 `item.text`）。
- Session resume 是**子指令**、不是 flag：
  `codex exec resume --last "..."` 或 `codex exec resume <SESSION_ID> "..."`
  （`SESSION_ID` 格式是 UUID，來自 `thread.started` 的 `thread_id`）。
  resume 子指令底下 `--json`/`--sandbox`/`--model`/`--cd` 這些 flag 能不能
  照樣加、還是會被忽略／繼承原 session 設定——文件沒寫清楚，這裡先假設
  可以照樣加，需要實測確認。
- 官方文件明確說明 `codex exec` **不會**暫停等待互動核准（headless 模式
  "never prompts"），唯一的安全控制是 `--sandbox` 等級——跟這次幫 Claude
  Team Run 驗證出來的「headless -p 模式沒有真正互動核准」是同一個結論。
  `workspace-write`（可寫入工作目錄，但不是完全不設防）在這裡的角色，
  對應 Claude 那邊選的 `acceptEdits`。
- 認證：`CODEX_API_KEY=<key>` 環境變數，只在 `codex exec` 模式生效
  （對應這個 codebase 既有的 `env["ANTHROPIC_API_KEY"] = api_key` 模式）。
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from helpers import safe_kill_process, wrap_cmd

from .base import RunResult

name = "codex"

DEFAULT_PERMISSION_MODE = "workspace-write"
VALID_PERMISSION_MODES = frozenset({"read-only", "workspace-write", "danger-full-access"})


def _codex_bin() -> str:
    for mod_name in ("main", "backend.main", "__main__"):
        mod = sys.modules.get(mod_name)
        if mod and hasattr(mod, "CODEX_BIN"):
            return getattr(mod, "CODEX_BIN", "codex")
    return "codex"


def _normalize_sandbox_mode(permission_mode: str) -> str:
    # permission_mode 有可能是呼叫端沿用 Claude 那邊的字彙（例如
    # "acceptEdits"）——這種情況不強行對應，直接退回 Codex 自己的預設值，
    # 避免把不合法的 --sandbox 值餵給 CLI。同一個 team 混用 Claude/Codex
    # 成員時會發生這種情況，所以這裡要能安全 fallback，不能直接丟例外。
    if permission_mode in VALID_PERMISSION_MODES:
        return permission_mode
    return DEFAULT_PERMISSION_MODE


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
    codex_bin = _codex_bin()
    safe_cwd = cwd if (cwd and Path(cwd).is_dir()) else str(Path.home())
    sandbox_mode = _normalize_sandbox_mode(permission_mode)

    if resume_session_id:
        cmd = [codex_bin, "exec", "resume", resume_session_id, prompt]
    else:
        cmd = [codex_bin, "exec", prompt]

    cmd += ["--json", "--sandbox", sandbox_mode, "--cd", safe_cwd]
    if model:
        cmd += ["--model", model]

    env = {**os.environ}
    if api_key:
        env["CODEX_API_KEY"] = api_key

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
                ev_type = ev.get("type")
                if ev_type == "thread.started" and ev.get("thread_id"):
                    session_id = ev["thread_id"]
                elif ev_type == "item.completed":
                    item = ev.get("item", {})
                    if item.get("type") == "agent_message":
                        chunk = item.get("text", "")
                        if chunk:
                            output_parts.append(chunk)
                            await on_text(chunk)
                elif ev_type == "turn.failed":
                    err_text = json.dumps(ev.get("error", ev), ensure_ascii=False)
                    return RunResult(
                        output="".join(output_parts), session_id=session_id,
                        error=f"turn.failed: {err_text}",
                    )
            except json.JSONDecodeError:
                pass
        await proc.wait()
    except Exception as e:
        return RunResult(output="".join(output_parts), session_id=session_id, error=str(e))

    return RunResult(output="".join(output_parts), session_id=session_id)
