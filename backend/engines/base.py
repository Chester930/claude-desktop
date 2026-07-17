"""
engines/base.py — 共用型別，定義每個 agent engine module 要提供的介面。

不用 abc.ABC／Protocol 強制約束，比照這個 codebase 其他地方（routes/*.py、
helpers.py）以「plain function + 約定俗成的簽名」為主的風格：每個
engines/<name>_engine.py 都要提供：

    name: str                      # 例如 "claude" / "codex"
    DEFAULT_PERMISSION_MODE: str    # 這個引擎自己的預設權限模式字彙
                                     # （Claude 是 "acceptEdits"，Codex 是
                                     # "workspace-write"，兩邊語彙不同，
                                     # 不強迫共用同一組列舉）
    async def run_turn(..., ) -> RunResult

呼叫端（routes/teams.py::_agent_run_capture）只依賴這個 run_turn 簽名，
不知道底下實際是哪個 CLI、什麼 flags、什麼輸出格式——這些細節全部封裝在
各自的 <name>_engine.py 裡。

prompt 組裝（agent frontmatter body、soul、memory context 的注入）刻意
不放進這一層——那是 Team/Agent/Memory 系統自己的邏輯，跟「這段 prompt
最後要丟給哪個 CLI 執行」是兩件事，engine 只負責「執行一輪對話、把文字
串流回來、回報 session id」。

2026-07-17 補上的 on_tool_event（見下方 OnToolEvent）：實測發現
claude_engine.py／codex_engine.py 原本都只把純文字（assistant text /
agent_message）餵給 on_text，工具呼叫的結構化資訊直接被丟掉——不是簡化
成文字，是完全沒有任何路徑處理它。用真實 CLI 對照過：Codex 的
`item.completed`/`item.started` 事件裡有 `command_execution`
（command/aggregated_output/exit_code/status）跟 `file_change`
（changes/status）這兩種已驗證存在的工具呼叫型別；Claude 的
`stream-json` 裡 assistant content block 也有 `tool_use`、user content
block 有 `tool_result`，只是舊版解析迴圈的 `if block.type == "text"`
判斷式直接跳過了它們。

on_tool_event 是新增的第二個「輸出」callback（跟 on_text 平行、不是取代）
：engine 呼叫時傳一個**已經組好的完整 envelope dict**（形狀跟
main.py::handle_chat 的 `_run_pooled`——已經在用、前端也已經在吃的
Claude SDK 原生路徑——完全一致：`{"type": "tool_use", "id", "name",
"input"}` 或 `{"type": "user", "message": {"content": [{"type":
"tool_result", "tool_use_id", "content"}]}}`），呼叫端（handle_chat／
_agent_run_capture）決定要怎麼處理這個 dict（直接轉發成 SSE，或是
格式化成一段文字塞進 team run 的 step_text）——engine 本身不知道也不
需要知道自己是被哪種呼叫端用。保留 Optional、預設 None：舊呼叫端不傳
這個參數，行為跟這次改動前完全一樣，不是破壞性變更。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Optional


@dataclass
class RunResult:
    """run_turn() 的回傳值。"""
    output: str = ""
    session_id: str = ""
    error: Optional[str] = None


# run_turn 的呼叫端傳入的 callback 型別，方便各 engine 模組互相參照一致的簽名。
OnText = Callable[[str], Awaitable[None]]
OnProcess = Callable[[Any], None]
IsCancelled = Callable[[], bool]
# engine 呼叫時傳入一個已經組好的完整事件 dict（見上方檔頭說明的兩種
# envelope 形狀）；呼叫端負責決定怎麼呈現，engine 只管「這是一次工具
# 呼叫／工具結果」，不管呈現方式。
OnToolEvent = Callable[[dict], Awaitable[None]]
