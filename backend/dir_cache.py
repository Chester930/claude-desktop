"""dir_cache.py — 目錄掃描快取（agents/skills/souls 用）。

handle_agents/handle_skills/handle_souls_list 每次都要整個目錄重新讀檔＋
解析 frontmatter，即使兩次呼叫之間什麼都沒變（實測過：445 個 skill 目錄
11 秒、291 個 soul 檔案 1.46 秒）。這裡用「每個項目自己的 mtime」當快取
key：目錄列表（scandir/glob + stat）本身很便宜，每次都重新掃；只有真的
被改過的項目（mtime 不一樣）才需要重新讀檔內容＋解析，沒變的直接沿用
上次快取結果。

刻意不用「只比對目錄本身的 mtime」這種更簡化的做法——目錄 mtime 只有
新增/刪除/改名項目時才會變，PUT 修改「既有檔案的內容」不會動到目錄
mtime，只會動到那個檔案自己的 mtime，用目錄 mtime 當唯一依據會漏掉這種
就地編輯，端點會回傳過期內容。

也刻意不用 watchdog 檔案監控——每個項目自己的 mtime 比對已經能正確處理
「這個 app 自己的 API 寫入」跟「外部直接編輯檔案」兩種情況（寫入一定會
更新檔案自己的 mtime），不需要額外背景執行緒監控檔案系統事件、也沒有
「監控啟動前的變動沒被記錄到」這種 watchdog 常見的邊界情況；壞處是還是
要每次都做一輪 stat()，但那比整個檔案讀出來解析 frontmatter 便宜非常多。

實測踩到的坑：stat() 本身在 Docker 的 Windows bind mount 上也不便宜——
445 個項目就算全部命中快取（不用重新讀檔+解析），單純同步跑一輪 stat()
還是量到 4 秒，而且這段迴圈是同步的，會卡住整個 event loop（不只慢，
還會讓其他請求在這幾秒內完全沒辦法被處理）。跟 build_one 一樣丟到
thread pool 平行跑，stat 這階段本身也要平行化，不能只平行化「重新讀檔」
那段。
"""

from __future__ import annotations

import asyncio
import threading
from pathlib import Path
from typing import Callable

_cache: "dict[str, dict[str, tuple[float, dict]]]" = {}
_lock = threading.Lock()


def _default_mtime(p: Path) -> float:
    return p.stat().st_mtime


def _safe_mtime(p: Path, mtime_fn: "Callable[[Path], float]") -> "float | None":
    try:
        return mtime_fn(p)
    except OSError:
        return None


async def cached_parallel_scan(
    cache_key: str,
    entries: "list[Path]",
    build_one: "Callable[[Path], dict | None]",
    mtime_fn: "Callable[[Path], float]" = _default_mtime,
) -> "list[dict]":
    """entries 是已經排序好的檔案/目錄清單；build_one(path) 是單一項目的
    同步建構函式（丟到 thread pool 執行），回傳 None 代表這個項目讀取/
    解析失敗、跳過。cache_key 用來區分不同目錄的快取（例如 registryHome
    切換後，同一個邏輯目錄會對應到不同的實際路徑，各自獨立快取）。

    mtime_fn 預設用項目自己的 mtime，但這對「目錄型」項目不夠：目錄的
    mtime 只有目錄底下的項目被新增/刪除/改名才會變，目錄裡某個檔案的
    內容被原地編輯（例如 skill 目錄裡的 SKILL.md 被 PUT 修改）不會動到
    目錄自己的 mtime，用預設值會漏掉這種變動。呼叫端如果有這種「目錄裡
    藏著真正內容檔案」的情況，要傳自訂的 mtime_fn（通常是目錄 mtime 跟
    內容檔案 mtime 取最大值）。"""
    mtimes = await asyncio.gather(*[asyncio.to_thread(_safe_mtime, e, mtime_fn) for e in entries])
    current_mtimes: "dict[str, float]" = {
        e.name: m for e, m in zip(entries, mtimes) if m is not None
    }

    with _lock:
        cache = _cache.setdefault(cache_key, {})
        for stale_name in set(cache) - set(current_mtimes):
            del cache[stale_name]
        to_rebuild = [
            e for e in entries
            if e.name in current_mtimes
            and (e.name not in cache or cache[e.name][0] != current_mtimes[e.name])
        ]
        hits = {
            name: entry[1]
            for name, entry in cache.items()
            if name in current_mtimes and name not in {e.name for e in to_rebuild}
        }

    if to_rebuild:
        built = await asyncio.gather(*[asyncio.to_thread(build_one, e) for e in to_rebuild])
        with _lock:
            for e, result in zip(to_rebuild, built):
                if result is not None:
                    cache[e.name] = (current_mtimes[e.name], result)
                    hits[e.name] = result
                else:
                    cache.pop(e.name, None)
                    hits.pop(e.name, None)

    return [hits[e.name] for e in entries if e.name in hits]


def invalidate(cache_key: "str | None" = None) -> None:
    """目前沒有呼叫端主動呼叫——mtime 比對本身就會抓到既有檔案被改過
    （write 一定會更新檔案自己的 mtime）。留著這個函式是給極端情況當
    保險用（例如手動改過系統時鐘、或想在測試裡強制清快取），不是正常
    運作流程必須依賴的路徑。"""
    with _lock:
        if cache_key is None:
            _cache.clear()
        else:
            _cache.pop(cache_key, None)
