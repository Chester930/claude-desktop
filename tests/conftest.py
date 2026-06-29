"""
pytest conftest — 建立暫存 claude home 並啟動測試用 aiohttp 伺服器

兼容 pytest-asyncio 0.23+ / 1.x 的 asyncio_default_fixture_loop_scope 設定：
  - app 採 function scope，避免 web.Application 被不同 event loop 綁定的問題
  - 檔案建立 (tmp_claude_home / sample_*) 仍為 session scope（純 sync，無 loop 綁定）
"""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest
import pytest_asyncio
from aiohttp.test_utils import TestClient, TestServer

# ── 把 backend/ 加入 sys.path ─────────────────────────────────────────────────
BACKEND_DIR = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))


# ── session-scoped 純 sync fixtures ──────────────────────────────────────────

@pytest.fixture(scope="session")
def tmp_claude_home(tmp_path_factory):
    """session 級別的暫存 ~/.claude 目錄，測試結束後自動清除"""
    base = tmp_path_factory.mktemp("claude_home")
    (base / "agents").mkdir()
    (base / "skills").mkdir()
    (base / "teams").mkdir()
    (base / "souls").mkdir()
    (base / "memory").mkdir()
    # 寫一個最基本的 config
    (base / "claude-desktop-config.json").write_text(
        json.dumps({"projectDir": "", "claudeHome": str(base)}),
        encoding="utf-8",
    )
    return base


@pytest.fixture(scope="session")
def sample_agent(tmp_claude_home):
    """建立一個測試用 agent .md 檔"""
    agent_file = tmp_claude_home / "agents" / "test-agent.md"
    agent_file.write_text(
        "---\n"
        "name: test-agent\n"
        "description: 用於測試的代理人\n"
        "tools: Read, Grep\n"
        "soul: \n"
        "skills:\n"
        "  - test-skill\n"
        "memory:\n"
        "  - test-memory-key\n"
        "mcp: []\n"
        "output_memory:\n"
        "  - test-output-key\n"
        "---\n\n## Test Agent\n\n這是測試代理人。\n",
        encoding="utf-8",
    )
    return agent_file


@pytest.fixture(scope="session")
def sample_skill(tmp_claude_home):
    """建立一個測試用 skill .md 檔"""
    skill_file = tmp_claude_home / "skills" / "test-skill.md"
    skill_file.write_text(
        "---\n"
        "name: test-skill\n"
        "description: 用於測試的技能\n"
        "mcp: []\n"
        "memory:\n"
        "  - project-conventions\n"
        "output_memory:\n"
        "  - skill-result\n"
        "---\n\n## Test Skill\n\n這是測試技能。\n",
        encoding="utf-8",
    )
    return skill_file


@pytest.fixture(scope="session")
def sample_team(tmp_claude_home):
    """建立一個測試用 team .yaml 檔"""
    team_file = tmp_claude_home / "teams" / "test-team.yaml"
    team_file.write_text(
        "name: test-team\n"
        "description: 用於測試的團隊\n"
        "members:\n"
        "  - agent: test-agent\n"
        "    role: 測試角色\n",
        encoding="utf-8",
    )
    return team_file


@pytest.fixture(scope="session")
def sample_memory(tmp_claude_home):
    """建立測試用 memory key"""
    mem_file = tmp_claude_home / "memory" / "test-memory-key.md"
    mem_file.write_text("# 測試記憶\n\n這是測試用的 memory 內容。\n", encoding="utf-8")
    return mem_file


# ── function-scoped async fixtures（避免 "different loop" 錯誤）──────────────

@pytest_asyncio.fixture
async def app(tmp_claude_home, sample_agent, sample_skill, sample_team, sample_memory):
    """每個測試函數都取得一個新 aiohttp Application 實例（以暫存 claude_home 覆蓋全域路徑）"""
    import main  # noqa: F401

    # 覆蓋全域路徑（每次都重設，確保 isolation）
    main.CLAUDE_HOME  = tmp_claude_home
    main.AGENTS_DIR   = tmp_claude_home / "agents"
    main.SKILLS_DIR   = tmp_claude_home / "skills"
    main.TEAMS_DIR    = tmp_claude_home / "teams"
    main.SOULS_DIR    = tmp_claude_home / "souls"
    main.CONFIG_FILE  = tmp_claude_home / "claude-desktop-config.json"

    # 重新初始化 DB（指向暫存目錄）
    main._INDEX_DB = tmp_claude_home / "claude-desktop-index.db"
    main._init_db()
    main._migrate_db()

    return main.build_app()


@pytest_asyncio.fixture
async def client(app):
    """每個測試函數都取得一個新的 TestClient（function scope，避免 loop 綁定問題）"""
    async with TestClient(TestServer(app)) as cli:
        yield cli
