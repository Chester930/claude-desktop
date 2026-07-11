"""2026-07-11：Agent 的 skills: [...] 欄位之前只是 metadata 標籤，從沒有人
把 skill 檔案的實際內容讀出來塞進 prompt——真正生效與否完全依賴底層 CLI
自己原生的 slash-skill 機制（Claude/Codex 讀的路徑還不一樣，Codex 那條
已知目前是壞的）。_read_skills_content() 讓 app 自己讀內容、手動折進
prompt，比照 _read_agent_body() 對 agent body 的做法，這樣 skill 對兩個
引擎都真正生效，不再依賴任何一邊 CLI 的原生載入機制。
"""
from pathlib import Path

from helpers import _read_skills_content


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_reads_single_file_skill_body(tmp_path):
    skills_dir = tmp_path / "skills"
    _write(skills_dir / "tdd.md", "---\ndescription: TDD 工作流\n---\n\n先寫測試再寫程式。")

    result = _read_skills_content(skills_dir, ["tdd"])

    assert "[Skill: tdd]" in result
    assert "先寫測試再寫程式。" in result


def test_reads_directory_skill_via_skill_md(tmp_path):
    skills_dir = tmp_path / "skills"
    _write(skills_dir / "web-design" / "SKILL.md", "---\ndescription: 網頁設計\n---\n\n注重可用性與對比度。")

    result = _read_skills_content(skills_dir, ["web-design"])

    assert "[Skill: web-design]" in result
    assert "注重可用性與對比度。" in result


def test_directory_skill_falls_back_to_readme(tmp_path):
    skills_dir = tmp_path / "skills"
    _write(skills_dir / "legacy-skill" / "README.md", "舊格式技能說明。")

    result = _read_skills_content(skills_dir, ["legacy-skill"])

    assert "舊格式技能說明。" in result


def test_multiple_skills_joined_with_separator(tmp_path):
    skills_dir = tmp_path / "skills"
    _write(skills_dir / "a.md", "技能 A 內容")
    _write(skills_dir / "b.md", "技能 B 內容")

    result = _read_skills_content(skills_dir, ["a", "b"])

    assert "技能 A 內容" in result
    assert "技能 B 內容" in result
    assert "\n\n---\n\n" in result


def test_missing_skill_silently_skipped(tmp_path):
    skills_dir = tmp_path / "skills"
    _write(skills_dir / "real.md", "真的存在")

    result = _read_skills_content(skills_dir, ["real", "does-not-exist"])

    assert "真的存在" in result
    assert "does-not-exist" not in result


def test_empty_skill_list_returns_empty_string(tmp_path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    assert _read_skills_content(skills_dir, []) == ""
    assert _read_skills_content(skills_dir, None) == ""


def test_path_traversal_id_rejected(tmp_path):
    skills_dir = tmp_path / "skills"
    _write(skills_dir / "real.md", "安全內容")
    outside = tmp_path / "secret.md"
    _write(outside, "不應該被讀到")

    result = _read_skills_content(skills_dir, ["../secret", "real"])

    assert "不應該被讀到" not in result
    assert "安全內容" in result
