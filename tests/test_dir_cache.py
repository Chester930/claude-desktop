"""
dir_cache.py 正確性測試 — agents/skills/souls 的 mtime 快取。

重點在「快取不能回傳過期內容」：新增/刪除容易驗證，真正容易漏掉的是
「既有檔案內容被原地修改」（PUT 修改同一個檔名）、以及「目錄型項目
（skill 目錄）裡的內容檔案被原地修改，但目錄自己的 mtime 沒變」這兩種
情況——這兩個都曾經是這個快取實作草稿裡的真實 bug（在正式進 main 前用
獨立腳本抓到的），所以特別各寫一個測試釘住。
"""
import time
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
import dir_cache


def _build_text(p: Path) -> dict:
    return {"id": p.stem, "content": p.read_text(encoding="utf-8")}


def _skill_mtime(e: Path) -> float:
    mtime = e.stat().st_mtime
    if e.is_dir():
        for name in ("SKILL.md", "README.md"):
            try:
                mtime = max(mtime, (e / name).stat().st_mtime)
            except OSError:
                pass
    return mtime


def _build_skill_dir(p: Path) -> dict:
    f = p / "SKILL.md"
    return {"id": p.name, "content": f.read_text(encoding="utf-8") if f.exists() else ""}


@pytest.fixture
def cache_key(tmp_path):
    """每個測試用獨一無二的 cache_key，避免測試之間互相污染模組級的
    _cache 字典（dir_cache 的快取是 process 全域的）。"""
    return f"test:{tmp_path}"


class TestDirCache:
    async def test_initial_scan(self, tmp_path, cache_key):
        (tmp_path / "a.md").write_text("hello a", encoding="utf-8")
        (tmp_path / "b.md").write_text("hello b", encoding="utf-8")
        entries = sorted(tmp_path.glob("*.md"))

        result = await dir_cache.cached_parallel_scan(cache_key, entries, _build_text)
        assert {x["id"]: x["content"] for x in result} == {"a": "hello a", "b": "hello b"}

    async def test_unchanged_rescan_matches(self, tmp_path, cache_key):
        (tmp_path / "a.md").write_text("hello a", encoding="utf-8")
        entries = sorted(tmp_path.glob("*.md"))

        r1 = await dir_cache.cached_parallel_scan(cache_key, entries, _build_text)
        r2 = await dir_cache.cached_parallel_scan(cache_key, entries, _build_text)
        assert r1 == r2

    async def test_in_place_edit_is_not_stale(self, tmp_path, cache_key):
        """健檢核心案例：PUT 修改既有檔案內容（檔名不變），下一次 GET
        一定要看到新內容，不能回傳快取住的舊內容。"""
        f = tmp_path / "a.md"
        f.write_text("v1", encoding="utf-8")
        entries = [f]
        r1 = await dir_cache.cached_parallel_scan(cache_key, entries, _build_text)
        assert r1[0]["content"] == "v1"

        time.sleep(0.05)  # 確保 mtime 有機會往前跳（部分檔案系統精度到秒）
        f.write_text("v2-EDITED", encoding="utf-8")
        r2 = await dir_cache.cached_parallel_scan(cache_key, entries, _build_text)
        assert r2[0]["content"] == "v2-EDITED"

    async def test_new_file_appears(self, tmp_path, cache_key):
        (tmp_path / "a.md").write_text("hello a", encoding="utf-8")
        entries = sorted(tmp_path.glob("*.md"))
        await dir_cache.cached_parallel_scan(cache_key, entries, _build_text)

        (tmp_path / "c.md").write_text("hello c", encoding="utf-8")
        entries = sorted(tmp_path.glob("*.md"))
        result = await dir_cache.cached_parallel_scan(cache_key, entries, _build_text)
        ids = {x["id"] for x in result}
        assert "c" in ids

    async def test_deleted_file_disappears(self, tmp_path, cache_key):
        f = tmp_path / "b.md"
        f.write_text("hello b", encoding="utf-8")
        entries = sorted(tmp_path.glob("*.md"))
        await dir_cache.cached_parallel_scan(cache_key, entries, _build_text)

        f.unlink()
        entries = sorted(tmp_path.glob("*.md"))
        result = await dir_cache.cached_parallel_scan(cache_key, entries, _build_text)
        assert result == []

    async def test_directory_type_skill_in_place_edit_is_not_stale(self, tmp_path, cache_key):
        """健檢第二個核心案例：skill 目錄的 mtime 只有新增/刪除/改名項目
        才會變，SKILL.md 內容被原地編輯不會動到目錄自己的 mtime——沒有
        自訂 mtime_fn 的話，這種編輯會被快取吃掉、端點回傳過期內容。"""
        skill_dir = tmp_path / "myskill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("v1", encoding="utf-8")
        entries = [skill_dir]

        r1 = await dir_cache.cached_parallel_scan(
            cache_key, entries, _build_skill_dir, mtime_fn=_skill_mtime
        )
        assert r1[0]["content"] == "v1"

        dir_mtime_before = skill_dir.stat().st_mtime
        time.sleep(0.05)
        (skill_dir / "SKILL.md").write_text("v2-EDITED", encoding="utf-8")
        # 驗證前提成立：目錄自己的 mtime 真的沒變（不然這個測試沒有測到
        # 我們真正想釘住的情境）
        assert skill_dir.stat().st_mtime == dir_mtime_before

        r2 = await dir_cache.cached_parallel_scan(
            cache_key, entries, _build_skill_dir, mtime_fn=_skill_mtime
        )
        assert r2[0]["content"] == "v2-EDITED"

    async def test_build_one_returning_none_is_excluded(self, tmp_path, cache_key):
        f = tmp_path / "bad.md"
        f.write_text("x", encoding="utf-8")
        entries = [f]

        result = await dir_cache.cached_parallel_scan(cache_key, entries, lambda p: None)
        assert result == []

    def test_invalidate_specific_key(self, tmp_path):
        key = f"test-invalidate:{tmp_path}"
        dir_cache._cache[key] = {"x": (123.0, {"id": "x"})}
        dir_cache.invalidate(key)
        assert key not in dir_cache._cache

    def test_invalidate_all(self, tmp_path):
        key = f"test-invalidate-all:{tmp_path}"
        dir_cache._cache[key] = {"x": (123.0, {"id": "x"})}
        dir_cache.invalidate()
        assert dir_cache._cache == {}
