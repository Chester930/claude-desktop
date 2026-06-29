"""
後端 API 整合測試 — 對應 ROADMAP.md 各 Phase 的核心端點

執行方式：
    cd claude-desktop
    pytest tests/ -v
"""
import json
import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.asyncio


# ══════════════════════════════════════════════════════════════════════════════
# 工具函數單元測試（不需要 HTTP server）
# ══════════════════════════════════════════════════════════════════════════════

class TestHelperFunctions:
    """ROADMAP Phase 1 — 工具函數測試"""

    def test_encode_slug_windows_path(self):
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
        import main
        slug = main._encode_slug("C:\\Users\\test\\project")
        assert "\\" not in slug
        assert ":" not in slug

    def test_encode_slug_unix_path(self):
        import main
        slug = main._encode_slug("/home/user/my-project")
        assert "/" not in slug

    def test_encode_slug_empty(self):
        import main
        assert main._encode_slug("") == ""

    def test_parse_yaml_simple_basic(self):
        import main
        result = main._parse_yaml_simple(
            "---\nname: test\ndescription: hello world\nskills: []\n---\n\nbody"
        )
        assert result.get("name") == "test"
        assert result.get("description") == "hello world"

    def test_parse_yaml_simple_list_values(self):
        import main
        result = main._parse_yaml_simple(
            "---\nskills:\n  - skill-a\n  - skill-b\nmemory: []\n---\n"
        )
        assert "skill-a" in result.get("skills", [])
        assert "skill-b" in result.get("skills", [])

    def test_parse_yaml_simple_no_frontmatter(self):
        import main
        result = main._parse_yaml_simple("just plain text without frontmatter")
        assert isinstance(result, dict)

    def test_agent_dict_parses_sample(self, tmp_claude_home, sample_agent):
        import main
        main.AGENTS_DIR = tmp_claude_home / "agents"
        d = main._agent_dict(sample_agent)
        assert d["name"] == "test-agent"
        assert "test-skill" in d.get("skills", [])
        assert "test-memory-key" in d.get("memory", [])
        assert "test-output-key" in d.get("output_memory", [])

    def test_team_dict_parses_sample(self, tmp_claude_home, sample_team):
        import main
        main.TEAMS_DIR = tmp_claude_home / "teams"
        d = main._team_dict(sample_team)
        assert d["name"] == "test-team"
        members = d.get("members", [])
        assert len(members) == 1
        assert members[0]["agent"] == "test-agent"


# ══════════════════════════════════════════════════════════════════════════════
# Phase 0 — 基礎健康檢查
# ══════════════════════════════════════════════════════════════════════════════

class TestHealthCheck:
    """GET /api/status"""

    async def test_status_ok(self, client):
        resp = await client.get("/api/status")
        assert resp.status == 200
        body = await resp.json()
        assert body["status"] == "ok"
        assert "claude_bin" in body
        assert "active_sessions" in body

    async def test_status_method_not_allowed(self, client):
        resp = await client.post("/api/status")
        assert resp.status == 405

    async def test_config_get(self, client):
        resp = await client.get("/api/config")
        assert resp.status == 200
        body = await resp.json()
        assert "_resolvedClaudeHome" in body


# ══════════════════════════════════════════════════════════════════════════════
# Phase 1 — Agent Mapping
# ══════════════════════════════════════════════════════════════════════════════

class TestAgentCRUD:
    """ROADMAP Phase 1 — Agent CRUD（P1-B1 ~ P1-B3, P1-M1 ~ P1-M2）"""

    async def test_list_agents_returns_list(self, client, sample_agent):
        resp = await client.get("/api/agents")
        assert resp.status == 200
        body = await resp.json()
        assert isinstance(body, list)
        # 應包含我們建立的 test-agent
        ids = [a["id"] for a in body]
        assert "test-agent" in ids

    async def test_get_single_agent(self, client, sample_agent):
        resp = await client.get("/api/agents/test-agent")
        assert resp.status == 200
        body = await resp.json()
        assert body["name"] == "test-agent"
        assert body["description"] == "用於測試的代理人"

    async def test_get_nonexistent_agent_404(self, client):
        resp = await client.get("/api/agents/does-not-exist-xyz")
        assert resp.status == 404

    async def test_create_agent(self, client, tmp_claude_home):
        import main
        main.AGENTS_DIR = tmp_claude_home / "agents"
        payload = {"name": "new-test-agent", "description": "動態建立的代理人"}
        resp = await client.post("/api/agents", json=payload)
        assert resp.status == 200
        body = await resp.json()
        assert body["ok"] is True
        assert body["id"] == "new-test-agent"
        # 確認檔案實際存在
        assert (tmp_claude_home / "agents" / "new-test-agent.md").exists()

    async def test_create_agent_duplicate_409(self, client, tmp_claude_home):
        import main
        main.AGENTS_DIR = tmp_claude_home / "agents"
        payload = {"name": "new-test-agent", "description": "重複建立"}
        resp = await client.post("/api/agents", json=payload)
        assert resp.status == 409

    async def test_update_agent_description(self, client, sample_agent):
        resp = await client.put(
            "/api/agents/test-agent",
            json={"description": "更新後的描述"},
        )
        assert resp.status == 200
        body = await resp.json()
        assert body["ok"] is True
        # 確認描述已更新
        resp2 = await client.get("/api/agents/test-agent")
        body2 = await resp2.json()
        assert body2["description"] == "更新後的描述"

    async def test_update_agent_skills(self, client, sample_agent):
        resp = await client.put(
            "/api/agents/test-agent",
            json={"skills": ["skill-a", "skill-b"]},
        )
        assert resp.status == 200
        # 讀回確認
        resp2 = await client.get("/api/agents/test-agent")
        body2 = await resp2.json()
        assert "skill-a" in body2.get("skills", [])

    async def test_delete_agent(self, client, tmp_claude_home):
        import main
        main.AGENTS_DIR = tmp_claude_home / "agents"
        # 先建立一個要刪除的 agent
        (tmp_claude_home / "agents" / "to-delete.md").write_text(
            "---\nname: to-delete\ndescription: 要刪除\n---\n", encoding="utf-8"
        )
        resp = await client.delete("/api/agents/to-delete")
        assert resp.status == 200
        assert not (tmp_claude_home / "agents" / "to-delete.md").exists()


# ══════════════════════════════════════════════════════════════════════════════
# Phase 1 — Skill CRUD
# ══════════════════════════════════════════════════════════════════════════════

class TestSkillCRUD:
    """ROADMAP Phase 1 — P1-S1 ~ P1-S8"""

    async def test_list_skills_returns_list(self, client, sample_skill):
        resp = await client.get("/api/skills")
        assert resp.status == 200
        body = await resp.json()
        assert isinstance(body, list)

    async def test_get_single_skill(self, client, sample_skill):
        resp = await client.get("/api/skills/test-skill")
        assert resp.status == 200
        body = await resp.json()
        assert body.get("name") == "test-skill"

    async def test_get_nonexistent_skill_404(self, client):
        resp = await client.get("/api/skills/ghost-skill-xyz")
        assert resp.status == 404

    async def test_update_skill(self, client, sample_skill, tmp_claude_home):
        import main
        main.SKILLS_DIR = tmp_claude_home / "skills"
        resp = await client.put(
            "/api/skills/test-skill",
            json={"description": "技能說明更新"},
        )
        assert resp.status == 200
        body = await resp.json()
        assert body["ok"] is True

    async def test_skill_has_output_memory_field(self, client, sample_skill):
        resp = await client.get("/api/skills/test-skill")
        body = await resp.json()
        assert "output_memory" in body


# ══════════════════════════════════════════════════════════════════════════════
# Phase 1 — Memory CRUD
# ══════════════════════════════════════════════════════════════════════════════

class TestMemoryCRUD:
    """ROADMAP Phase 1 — Memory 讀寫，及 Phase 3.C Memory Relay"""

    async def test_list_memory_returns_list(self, client, sample_memory):
        resp = await client.get("/api/memory")
        assert resp.status == 200
        body = await resp.json()
        assert isinstance(body, list)

    async def test_write_memory_key(self, client, tmp_claude_home):
        import main
        main.CLAUDE_HOME = tmp_claude_home

        resp = await client.put(
            "/api/memory/relay-test-key",
            json={"content": "# Relay Content\n\n這是 memory relay 測試內容"},
        )
        assert resp.status == 200
        # 確認檔案存在
        key_file = tmp_claude_home / "memory" / "relay-test-key.md"
        assert key_file.exists()
        assert "relay" in key_file.read_text(encoding="utf-8").lower()

    async def test_delete_memory_key(self, client, tmp_claude_home):
        import main
        main.CLAUDE_HOME = tmp_claude_home
        # 先建立
        mem_file = tmp_claude_home / "memory" / "del-test.md"
        mem_file.write_text("content", encoding="utf-8")
        resp = await client.delete("/api/memory/del-test")
        assert resp.status == 200
        assert not mem_file.exists()

    async def test_memory_relay_file_created_after_write(self, client, tmp_claude_home):
        """Phase 3.C：Memory 中繼驗證 — 寫入後可讀回相同內容"""
        import main
        main.CLAUDE_HOME = tmp_claude_home
        content = "Agent A 的輸出結果"
        await client.put("/api/memory/step1-result", json={"content": content})
        mem_file = tmp_claude_home / "memory" / "step1-result.md"
        assert mem_file.exists()
        assert content in mem_file.read_text(encoding="utf-8")


# ══════════════════════════════════════════════════════════════════════════════
# Phase 2 — Teams CRUD
# ══════════════════════════════════════════════════════════════════════════════

class TestTeamsCRUD:
    """ROADMAP Phase 2 — P2-B1, P2-B2"""

    async def test_list_teams_returns_list(self, client, sample_team):
        resp = await client.get("/api/teams")
        assert resp.status == 200
        body = await resp.json()
        assert isinstance(body, list)

    async def test_get_single_team(self, client, sample_team):
        resp = await client.get("/api/teams/test-team")
        assert resp.status == 200
        body = await resp.json()
        assert body["name"] == "test-team"
        assert isinstance(body["members"], list)

    async def test_get_nonexistent_team_404(self, client):
        resp = await client.get("/api/teams/no-such-team")
        assert resp.status == 404

    async def test_create_team(self, client, tmp_claude_home):
        import main
        main.TEAMS_DIR = tmp_claude_home / "teams"
        payload = {
            "name": "dyn-team",
            "description": "動態建立的團隊",
            "members": [{"agent": "test-agent", "role": "主要執行者"}],
        }
        resp = await client.post("/api/teams", json=payload)
        assert resp.status == 200
        body = await resp.json()
        assert body["ok"] is True
        assert (tmp_claude_home / "teams" / "dyn-team.yaml").exists()

    async def test_create_team_duplicate_409(self, client, tmp_claude_home):
        import main
        main.TEAMS_DIR = tmp_claude_home / "teams"
        payload = {"name": "dyn-team", "description": "重複"}
        resp = await client.post("/api/teams", json=payload)
        assert resp.status == 409

    async def test_update_team(self, client, tmp_claude_home):
        import main
        main.TEAMS_DIR = tmp_claude_home / "teams"
        resp = await client.put(
            "/api/teams/test-team",
            json={"description": "更新後的團隊描述"},
        )
        assert resp.status == 200
        body = await resp.json()
        assert body["ok"] is True

    async def test_delete_team(self, client, tmp_claude_home):
        import main
        main.TEAMS_DIR = tmp_claude_home / "teams"
        (tmp_claude_home / "teams" / "to-del-team.yaml").write_text(
            "name: to-del-team\ndescription: del\nmembers: []\n",
            encoding="utf-8",
        )
        resp = await client.delete("/api/teams/to-del-team")
        assert resp.status == 200
        assert not (tmp_claude_home / "teams" / "to-del-team.yaml").exists()

    async def test_team_members_structure(self, client, sample_team):
        resp = await client.get("/api/teams/test-team")
        body = await resp.json()
        for member in body["members"]:
            assert "agent" in member
            assert "role" in member


# ══════════════════════════════════════════════════════════════════════════════
# Phase 3 — Team Run（序列流水線）
# ══════════════════════════════════════════════════════════════════════════════

class TestTeamRun:
    """ROADMAP Phase 3 — P3-B1 ~ P3-B5"""

    async def test_team_run_requires_task(self, client):
        resp = await client.post("/api/team/run", json={"team_id": "test-team"})
        assert resp.status == 400
        body = await resp.json()
        assert "error" in body

    async def test_team_run_nonexistent_team_404(self, client, tmp_claude_home):
        import main
        main.TEAMS_DIR = tmp_claude_home / "teams"
        resp = await client.post(
            "/api/team/run",
            json={"team_id": "ghost-team", "task": "some task"},
        )
        assert resp.status == 404

    async def test_team_run_with_inline_team_payload(self, client, tmp_claude_home):
        """使用 team payload 而非 team_id，驗證 run_id 生成"""
        import main
        main.TEAMS_DIR = tmp_claude_home / "teams"
        # 使用 inline team payload（無須 claude 實際執行，因為 agent 不存在）
        payload = {
            "task": "測試任務描述",
            "team": {
                "name": "inline-team",
                "members": [
                    {"agent": "fake-agent-x", "role": "測試角色"},
                ],
            },
        }
        resp = await client.post("/api/team/run", json=payload)
        assert resp.status == 200
        body = await resp.json()
        assert body["ok"] is True
        assert "run_id" in body
        assert len(body["run_id"]) == 8  # hex[:8]

    async def test_team_run_get_status(self, client, tmp_claude_home):
        """建立 run 後立即查詢狀態"""
        import main
        main.TEAMS_DIR = tmp_claude_home / "teams"
        # 建立 run
        payload = {
            "task": "查詢狀態測試",
            "team": {
                "name": "status-team",
                "members": [{"agent": "fake-agent-y", "role": "狀態查詢"}],
            },
        }
        resp = await client.post("/api/team/run", json=payload)
        run_id = (await resp.json())["run_id"]

        # 查詢狀態
        resp2 = await client.get(f"/api/team/run/{run_id}")
        assert resp2.status == 200
        body2 = await resp2.json()
        assert body2["id"] == run_id
        assert "status" in body2
        assert "steps" in body2
        assert isinstance(body2["steps"], list)

    async def test_team_run_invalid_id_404(self, client):
        resp = await client.get("/api/team/run/nonexistent-run-id")
        assert resp.status == 404

    async def test_team_run_cancel(self, client, tmp_claude_home):
        import main
        main.TEAMS_DIR = tmp_claude_home / "teams"
        # 建立一個 run
        payload = {
            "task": "取消測試",
            "team": {
                "name": "cancel-team",
                "members": [{"agent": "fake-agent-z", "role": "取消"}],
            },
        }
        resp = await client.post("/api/team/run", json=payload)
        run_id = (await resp.json())["run_id"]
        # 取消
        resp2 = await client.delete(f"/api/team/run/{run_id}")
        assert resp2.status == 200


# ══════════════════════════════════════════════════════════════════════════════
# Phase 4 — HR Agent（自動組隊）
# ══════════════════════════════════════════════════════════════════════════════

class TestHRAgent:
    """ROADMAP Phase 4 — P4-B1 ~ P4-B3"""

    async def test_agents_registry_returns_list(self, client, sample_agent, tmp_claude_home):
        """GET /api/agents/registry 應回傳帶有 description 與 skills 的列表"""
        import main
        main.AGENTS_DIR = tmp_claude_home / "agents"
        resp = await client.get("/api/agents/registry")
        assert resp.status == 200
        body = await resp.json()
        assert isinstance(body, list)
        # 找到我們的 test-agent
        agent_ids = [a["id"] for a in body]
        assert "test-agent" in agent_ids
        # 每筆 registry 項目必須有 name / description / skills
        for item in body:
            assert "id" in item
            assert "name" in item
            assert "description" in item
            assert "skills" in item
            assert isinstance(item["skills"], list)

    async def test_agents_registry_empty_when_no_agents(self, client, tmp_claude_home):
        """如果 agents 目錄下沒有 .md 檔，回傳空列表"""
        import main
        # 暫時指向空目錄
        empty_dir = tmp_claude_home / "agents_empty"
        empty_dir.mkdir(exist_ok=True)
        original = main.AGENTS_DIR
        main.AGENTS_DIR = empty_dir
        resp = await client.get("/api/agents/registry")
        body = await resp.json()
        assert body == []
        main.AGENTS_DIR = original

    async def test_hr_dispatch_requires_task(self, client):
        """POST /api/hr/dispatch 不帶 task 應回傳 400"""
        resp = await client.post("/api/hr/dispatch", json={})
        assert resp.status == 400
        body = await resp.json()
        assert "error" in body

    async def test_hr_dispatch_no_agents_500(self, client, tmp_claude_home):
        """沒有任何 agent 時 HR dispatch 應回傳錯誤（不需要呼叫 Claude CLI）"""
        import main
        empty_dir = tmp_claude_home / "agents_empty"
        empty_dir.mkdir(exist_ok=True)
        original = main.AGENTS_DIR
        main.AGENTS_DIR = empty_dir
        resp = await client.post("/api/hr/dispatch", json={"task": "任意任務"})
        body = await resp.json()
        # 預期 500 + error 含有「尚未建立」
        assert resp.status == 500
        assert "error" in body
        assert "Agent" in body["error"] or "agent" in body["error"].lower()
        main.AGENTS_DIR = original


# ══════════════════════════════════════════════════════════════════════════════
# Phase 3 — Sessions & FTS
# ══════════════════════════════════════════════════════════════════════════════

class TestSessions:
    """Session 列表 + FTS 全文搜尋"""

    async def test_list_sessions_ok(self, client):
        resp = await client.get("/api/sessions")
        assert resp.status == 200
        body = await resp.json()
        assert "sessions" in body
        assert "total" in body

    async def test_sessions_search_returns_valid_structure(self, client):
        resp = await client.get("/api/sessions?q=test")
        assert resp.status == 200
        body = await resp.json()
        assert "sessions" in body
        assert isinstance(body["sessions"], list)

    async def test_sessions_pagination_offset(self, client):
        resp = await client.get("/api/sessions?offset=0")
        assert resp.status == 200

    async def test_delete_nonexistent_session(self, client):
        resp = await client.delete("/api/sessions/nonexistent-session-id-xyz")
        # 刪除不存在的 session 應不 crash（graceful）
        assert resp.status in (200, 404)


# ══════════════════════════════════════════════════════════════════════════════
# Phase 1 — Souls
# ══════════════════════════════════════════════════════════════════════════════

class TestSouls:
    """Soul 靈魂人格讀寫"""

    async def test_list_souls(self, client, tmp_claude_home):
        import main
        main.SOULS_DIR = tmp_claude_home / "souls"
        resp = await client.get("/api/souls")
        assert resp.status == 200
        body = await resp.json()
        assert isinstance(body, list)

    async def test_get_soul_content(self, client, tmp_claude_home):
        import main
        main.SOULS_DIR = tmp_claude_home / "souls"
        # 建立一個 soul 檔
        (tmp_claude_home / "souls" / "test-soul.md").write_text(
            "---\nname: test-soul\n---\n\n靈魂內容", encoding="utf-8"
        )
        resp = await client.get("/api/souls")
        body = await resp.json()
        # 至少有一個 soul
        assert len(body) >= 1

    async def test_save_soul(self, client, tmp_claude_home):
        import main
        main.SOULS_DIR = tmp_claude_home / "souls"
        resp = await client.put(
            "/api/souls/test-soul",
            json={"content": "# 更新的靈魂\n\n更新後的靈魂描述"},
        )
        assert resp.status == 200


# ══════════════════════════════════════════════════════════════════════════════
# Config / Schedules
# ══════════════════════════════════════════════════════════════════════════════

class TestConfigAndSchedules:
    """設定檔與排程讀寫"""

    async def test_config_get_has_required_fields(self, client):
        resp = await client.get("/api/config")
        body = await resp.json()
        assert "_resolvedClaudeHome" in body

    async def test_config_put_projectDir(self, client, tmp_claude_home):
        import main
        main.CONFIG_FILE = tmp_claude_home / "claude-desktop-config.json"
        resp = await client.put("/api/config", json={"projectDir": "/tmp/test-project"})
        assert resp.status == 200
        body = await resp.json()
        assert body["ok"] is True

    async def test_schedules_get(self, client):
        resp = await client.get("/api/schedules")
        assert resp.status == 200
        body = await resp.json()
        assert isinstance(body, list)

    async def test_schedules_post(self, client):
        resp = await client.post(
            "/api/schedules",
            json={
                "name": "Test Schedule",
                "cron": "0 9 * * *",
                "prompt": "每日早上的測試提示",
                "enabled": False,
            },
        )
        assert resp.status == 200
        body = await resp.json()
        assert "id" in body

    async def test_schedules_delete(self, client):
        # 先建立再刪除
        resp = await client.post(
            "/api/schedules",
            json={"name": "To Delete", "cron": "* * * * *", "prompt": "del", "enabled": False},
        )
        sid = (await resp.json())["id"]
        resp2 = await client.delete(f"/api/schedules/{sid}")
        assert resp2.status == 200


# ══════════════════════════════════════════════════════════════════════════════
# Phase 2 — Debug & Stats
# ══════════════════════════════════════════════════════════════════════════════

class TestDebugAndStats:
    """診斷 / 統計端點"""

    async def test_debug_dump_structure(self, client):
        """debug-dump 使用 Content-Disposition:attachment，用 text() 解析避免 content-type 問題"""
        import json as _json
        resp = await client.get("/api/debug-dump")
        assert resp.status == 200
        text = await resp.text()
        body = _json.loads(text)
        assert "timestamp" in body
        assert "platform" in body
        assert "sqlite" in body

    async def test_stats_endpoint(self, client):
        resp = await client.get("/api/stats")
        assert resp.status == 200
        body = await resp.json()
        assert isinstance(body, dict)
        # 核心統計欄位
        assert "sessions" in body
        assert "total_tokens" in body
        assert "heatmap" in body

    async def test_logs_endpoint(self, client):
        resp = await client.get("/api/logs")
        assert resp.status == 200
        body = await resp.json()
        assert "logs" in body
        assert isinstance(body["logs"], list)

    async def test_profiles_endpoint(self, client):
        resp = await client.get("/api/profiles")
        assert resp.status == 200
        body = await resp.json()
        assert "profiles" in body
        assert isinstance(body["profiles"], list)
        # 可能有 current 欄位
        assert "current" in body

    async def test_telegram_get_endpoint(self, client):
        resp = await client.get("/api/telegram")
        assert resp.status == 200
        body = await resp.json()
        assert "enabled" in body
        assert "token" in body
        assert "running" in body


# ══════════════════════════════════════════════════════════════════════════════
# ROADMAP 8.2 — 流水線完整性測試（無 Claude CLI）
# ══════════════════════════════════════════════════════════════════════════════

class TestTeamPipelineIntegrity:
    """ROADMAP 8.2 — Team 流水線完整性（不依賴 Claude CLI）"""

    async def test_team_run_step_structure(self, client, tmp_claude_home):
        """建立後立即查詢，steps 結構應正確"""
        import main
        main.TEAMS_DIR = tmp_claude_home / "teams"
        payload = {
            "task": "流水線結構測試",
            "team": {
                "name": "pipeline-test-team",
                "members": [
                    {"agent": "agent-a", "role": "第一步"},
                    {"agent": "agent-b", "role": "第二步"},
                ],
            },
        }
        resp = await client.post("/api/team/run", json=payload)
        assert resp.status == 200
        run_id = (await resp.json())["run_id"]

        resp2 = await client.get(f"/api/team/run/{run_id}")
        body = await resp2.json()
        assert len(body["steps"]) == 2
        assert body["steps"][0]["agent"] == "agent-a"
        assert body["steps"][1]["agent"] == "agent-b"
        # 每個 step 必須有 status 欄位
        for step in body["steps"]:
            assert "status" in step
            assert "role" in step

    async def test_team_run_task_stored(self, client, tmp_claude_home):
        """task 描述應儲存在 run 狀態裡"""
        import main
        main.TEAMS_DIR = tmp_claude_home / "teams"
        task_text = "驗證任務儲存的測試描述 UNIQUE_MARKER"
        payload = {
            "task": task_text,
            "team": {
                "name": "task-storage-team",
                "members": [{"agent": "agent-c", "role": "儲存驗證"}],
            },
        }
        resp = await client.post("/api/team/run", json=payload)
        run_id = (await resp.json())["run_id"]
        resp2 = await client.get(f"/api/team/run/{run_id}")
        body = await resp2.json()
        assert body["task"] == task_text

    async def test_team_run_uses_named_team(self, client, sample_team, tmp_claude_home):
        """用 team_id 啟動已存在的 team，應成功建立 run"""
        import main
        main.TEAMS_DIR = tmp_claude_home / "teams"
        payload = {"task": "使用具名 team 的任務", "team_id": "test-team"}
        resp = await client.post("/api/team/run", json=payload)
        assert resp.status == 200
        body = await resp.json()
        assert body["ok"] is True
