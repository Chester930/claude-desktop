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
