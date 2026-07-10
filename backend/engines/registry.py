"""
engines/registry.py — 引擎名稱 → 模組的對照表，以及「該用哪個引擎」的解析順序。

解析順序（優先序由高到低）：
1. Agent frontmatter 裡個別宣告的 `engine:`（同一個 team 混用 Claude/Codex
   成員時，這裡就是每個成員各自的選擇）。
2. 呼叫端（例如 POST /api/team/run 的 `agent_engine` 欄位）傳入的預設值。
3. DEFAULT_ENGINE_NAME（"claude"）。
"""

from __future__ import annotations

from . import claude_engine, codex_engine

ENGINES = {
    claude_engine.name: claude_engine,
    codex_engine.name: codex_engine,
}

DEFAULT_ENGINE_NAME = "claude"


def resolve_engine_name(frontmatter_engine: str, request_engine: str) -> str:
    for candidate in (frontmatter_engine, request_engine):
        if candidate and candidate in ENGINES:
            return candidate
    return DEFAULT_ENGINE_NAME


def get_engine(engine_name: str):
    return ENGINES.get(engine_name, ENGINES[DEFAULT_ENGINE_NAME])
