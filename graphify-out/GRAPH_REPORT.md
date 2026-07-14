# Graph Report - .  (2026-07-14)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2044 nodes · 3478 edges · 148 communities (97 shown, 51 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 401 edges (avg confidence: 0.66)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5d0b8c45`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- App
- helpers.py
- ClaudeService
- main.build_app() / AGENTS_DIR/SKILLS_DIR/TEAMS_DIR/SOULS_DIR/CONFIG_FILE globals
- app.ts
- codex_usage.py
- frontend
- ResourceSyncService
- test_engine_availability.py
- base.py
- database.py
- main.js
- .showToast
- SessionPool class — pooled ClaudeSDKClient connections
- .get
- _set_config
- mcp_sync.sync_add() — sync new MCP def to Claude/Codex CLIs
- main.py
- .addChatTab
- safe_kill_process
- TestMemviewAPI
- App Shell Component Template (app.html)
- teams.py
- MemoryAgent
- test_engine_registry.py
- TestIsSafeDockerIdent
- register_team_routes
- test_engine_mode_lockdown.py
- test_hr_dispatch_execution_mode.py
- apply_availability_fallback
- _load_config
- conftest.py
- MessageBus
- Session
- devDependencies
- dependencies
- RunResult dataclass (engine turn result contract)
- engines.registry.resolve_engine_name_gated
- TestAdversarialDebate
- TestAgentCRUD
- test_codex_api_key_and_bin_override.py
- TestTeamRunPathTraversalRejected
- registry.py
- scripts
- test_backend.py
- TestHelperFunctions
- test_mcp_sync.py
- run_import
- database.get_engine_mode
- engines.codex_engine.run_turn
- handle_schedules_post
- _resolve_agent_engine_and_key
- package.json
- test_mcp_servers_routes.py
- _agent_run_capture (routes/teams.py)
- build_team_memory_context
- engines.registry.resolve_engine_name_gated
- files
- TestTeamsCRUD
- TestHRAgent
- test_line_webhook_auth.py
- TestRestoreZipBomb
- _FakeStdout
- _FakeStdout
- test_upgrade.py
- TestTeamFailsafe
- engines.claude_engine.run_turn
- handle_mcp_rpc
- scripts
- build
- TestTeamRun
- test_database.py
- TestSessionSnippetEscaping
- _PersistentSessions
- TestSessionAdvanced
- TestConfigAndSchedules
- FakeService
- handle_run_artifacts
- TestSkillCRUD
- TestMemoryCRUD
- TestDebugAndStats
- TestSchedulePatch
- _FakeStdout
- test_team_run_execution_mode.py
- test_team_run_process_tracking.py
- _CustomModule — dynamic cross-instance database state sync pattern
- api getter (same-origin vs Electron port fallback)
- nsis
- TestSessions
- _FakeStdin
- test_team_run_permission_mode.py
- test_db_ctx.py - _db_ctx() context manager test suite
- frontend/package.json (scripts: start/build/test/e2e)
- package.json
- Researcher Agent (Soul Persona)
- TestSoulAdvanced
- test_db_ctx.py
- test_team_run_error_handling.py
- TestRunArtifactsTracer
- _cleanup_old_runs
- Team Run UI logic (_dispatchTeamRun/_applyTeamRunEvent)
- test_mcp_docker_hardening.py - Docker MCP security hardening test suite
- linux
- mac
- publish
- test_resource_sync_routes.py - /api/resource-sync route test suite
- test_agency_importer_hardening.py
- test_engine_status_route.py
- test_memory_agent_toctou.py
- tsconfig.json (base, references app/spec)
- test_line_webhook_auth.py - LINE webhook signature verification test suite
- test_memory_agent_toctou.py - MemoryAgent TOCTOU race condition test suite
- TestAgentDictEngineField
- test_team_run_consensus_members.py
- marked
- docker-entrypoint.sh
- cleanup_subprocesses() — atexit/signal child process reaper
- get_agent_soul
- McpServerDef interface
- SKILL_MCPS_MAP hardcoded skill->MCP mapping
- streamChat() SSE fetch method
- highlight.js
- tslib
- HR auto-team dispatch (dispatchHR/submitHRTeamRun)
- onChatClick() code-block copy handler
- message_bus.MessageBus
- start.sh
- test_codex_engine_real_invalid_model_scenario
- test_codex_engine_resume_omits_sandbox_and_cd_flags
- test_codex_engine_image_attachments_use_dash_i_flag
- SessionPool hardening test suite (T24)
- _is_safe_id() path traversal guard
- _safe_write_text() atomic write helper
- SQLite session index (sessions / sessions_fts trigram)
- handle_team_execute() — project-based team execution
- ChatTab interface
- CodexUsageError exception
- docker-entrypoint.sh (Codex runtime bootstrap)
- Electron App Icon (Claude Desktop)
- .vscode/extensions.json (recommends angular.ng-template)
- MessageBus singleton pub/sub
- VSCode Workspace Settings

## God Nodes (most connected - your core abstractions)
1. `App` - 278 edges
2. `ClaudeService` - 93 edges
3. `main.build_app() / AGENTS_DIR/SKILLS_DIR/TEAMS_DIR/SOULS_DIR/CONFIG_FILE globals` - 89 edges
4. `MemoryAgent` - 26 edges
5. `_agent_run_capture() — pluggable engine dispatch per agent` - 23 edges
6. `safe_kill_process()` - 22 edges
7. `ResourceSyncService` - 20 edges
8. `SessionPool class — pooled ClaudeSDKClient connections` - 19 edges
9. `helpers.wrap_cmd() — Windows .cmd shim wrapper` - 18 edges
10. `_execute_team_run_core() — parallel/sequential/consensus execution engine` - 18 edges

## Surprising Connections (you probably didn't know these)
- `後端 API 端點 (port 8765)` --references--> `GET /api/config endpoint`  [INFERRED]
  README.md → tests/test_secret_redaction.py
- `Phase 3 — Multi-Agent 序列執行` --conceptually_related_to--> `handle_team_run_post (routes/teams.py, POST /api/team/run)`  [INFERRED]
  ROADMAP.md → tests/test_team_run_execution_mode.py
- `importAgencyAgents() -> POST /api/agents/import-agency` --conceptually_related_to--> `agency_agents_importer._is_safe_id()`  [AMBIGUOUS]
  frontend/src/app/claude.service.ts → backend/agency_agents_importer.py
- `test_get_archival_memory_survives_vanishing_project_file()` --calls--> `MemoryAgent`  [INFERRED]
  tests/test_memory_agent_toctou.py → backend/memory_agent.py
- `test_safe_mtime_falls_back_when_file_vanishes()` --calls--> `MemoryAgent`  [INFERRED]
  tests/test_memory_agent_toctou.py → backend/memory_agent.py

## Import Cycles
- None detected.

## Communities (148 total, 51 thin omitted)

### Community 0 - "App"
Cohesion: 0.02
Nodes (3): Component, App, ViewChild

### Community 1 - "helpers.py"
Cohesion: 0.07
Nodes (63): _agent_dict(), _agent_dict_safe(), _desc_from_md_file(), _desc_from_skill_dir(), _parse_frontmatter_desc(), _parse_full_frontmatter(), _parse_yaml_list(), _parse_yaml_simple() (+55 more)

### Community 3 - "main.build_app() / AGENTS_DIR/SKILLS_DIR/TEAMS_DIR/SOULS_DIR/CONFIG_FILE globals"
Cohesion: 0.09
Nodes (58): _agent_memory_dir(), _global_memory_dir(), _init_db(), _memory_dir(), ~/.claude/memory/ — 全域公共記憶根目錄, ~/.claude/memory/agents/<id>/, ~/.claude/memory/teams/<id>/, Return ~/.claude/projects/<slug>/memory/ for the configured projectDir.     Fal (+50 more)

### Community 4 - "app.ts"
Cohesion: 0.06
Nodes (34): dompurify, dompurify, appConfig, Item, McpServer, McpTool, McpType, McpWorkflow (+26 more)

### Community 5 - "codex_usage.py"
Cohesion: 0.05
Nodes (34): Angular ApplicationConfig (bootstrap providers), flushInitialRequests() mock HTTP responder, App component test suite, CodexUsageError, codex_usage.fetch_codex_usage(), codex_usage.normalize_codex_usage(), Any, Process (+26 more)

### Community 6 - "frontend"
Cohesion: 0.05
Nodes (45): build, serve, test, builder, configurations, defaultConfiguration, options, cli (+37 more)

### Community 7 - "ResourceSyncService"
Cohesion: 0.10
Nodes (30): _agent_equivalent(), _agent_toml(), _frontmatter_and_body(), Path, Safe Agent/Skill deployment from Agent Desktop's Claude home to Codex.  Agent De, Inspect and deploy Claude-home Agents/Skills to Codex native paths., Fast identity used by status/dry-run; assets are read only when syncing., ResourceSyncService (+22 more)

### Community 8 - "test_engine_availability.py"
Cohesion: 0.08
Nodes (30): _FakeStdout, _make_fake_create_subprocess_exec(), 2026-07-11：engines/availability.py 的可用性偵測與 fallback 邏輯。  這裡全部 mock 掉 asyncio.c, Exit code 0 但輸出文字不含 "logged in"——fail closed，不當作已登入。, allowed 用預設值（兩邊都候選）時，「兩邊都不可用」的訊息要維持原本     的通用文字，不要被鎖定模式的訊息覆蓋掉——這條測試釘住預設路徑的既有, test_apply_availability_fallback_locked_codex_does_not_fall_over_to_claude(), test_apply_availability_fallback_neither_available_message_unaffected_by_default_allowed(), test_apply_availability_fallback_neither_available_raises() (+22 more)

### Community 9 - "base.py"
Cohesion: 0.07
Nodes (36): engines/base.py — 共用型別，定義每個 agent engine module 要提供的介面。  不用 abc.ABC／Protocol 強, 2026-07-11：Agent 的 skills: [...] 欄位之前只是 metadata 標籤，從沒有人 把 skill 檔案的實際內容讀出來塞進 p, 同一份 skill 內容注入邏輯要對 Codex 引擎一樣生效——這正是這次要修的     問題本身：skill 內容以前完全依賴 Claude CLI 自己, test_agent_run_capture_folds_skill_content_into_prompt_for_claude(), test_agent_run_capture_folds_skill_content_into_prompt_for_codex(), _write_agent(), _write_skill(), 2026-07-11：handle_chat（主聊天室，選了某個 agent 之後打字聊天）之前 完全沒有讀取 agent 的 engine: frontma (+28 more)

### Community 10 - "database.py"
Cohesion: 0.08
Nodes (39): _all_session_files(), _backfill_project_paths(), _db(), _db_ctx(), _find_session_file(), _migrate_db(), _migrate_fts_tokenizer(), _parse_jsonl_session() (+31 more)

### Community 11 - "main.js"
Cohesion: 0.06
Nodes (30): backend/main.py (aiohttp app entrypoint, restarted by watcher), _Handler (FileSystemEventHandler) — .py change detector, watcher restart loop (subprocess.Popen main.py), ALLOWED_EXTERNAL_PROTOCOLS, isAllowedExternalUrl() / ALLOWED_EXTERNAL_PROTOCOLS guard, { app, BrowserWindow, shell, Tray, Menu, nativeImage, dialog, ipcMain, Notification, safeStorage }, bundledExe, bundledFrontend (+22 more)

### Community 13 - "SessionPool class — pooled ClaudeSDKClient connections"
Cohesion: 0.07
Nodes (16): Pool of persistent ClaudeSDKClient connections, keyed by session key.  Replace, 呼叫端查詢完成後呼叫（成功或失敗都要），標記這個 key 不再忙碌，         並刷新 last-used 時間，避免長 turn 結束當下立刻被判定為, Background task: periodically evict connections idle past the timeout., run_idle_pruner(), SessionPool class — pooled ClaudeSDKClient connections, claude_agent_sdk.ClaudeSDKClient / ClaudeAgentOptions, ClaudeAgentOptions, ClaudeSDKClient (+8 more)

### Community 15 - "_set_config"
Cohesion: 0.07
Nodes (28): architect-agent, code-architect-skill, Agent 桌面版 (project README), 後端 API 端點 (port 8765), Docker 架構 (Electron + nginx/frontend + Python backend + ngrok), LINE Bot 設定 (Messaging API Channel), fetch (MCP), researcher-agent (+20 more)

### Community 16 - "mcp_sync.sync_add() — sync new MCP def to Claude/Codex CLIs"
Cohesion: 0.11
Nodes (29): main.py handle_mcp_action / handle_local_mcp_config_* (Docker/compose runtime lifecycle), _claude_add_args(), _claude_bin(), _codex_add_args(), _codex_bin(), mcp_sync.py — 把 app 自己的 MCP server 定義（backend/database.py 的 `_load_mcp_servers(, 把一個 MCP server 定義同步到兩邊 CLI。回傳 {"claude": bool, "codex": bool}，     某一邊失敗不影響另一邊、, 把一個 MCP server 從兩邊 CLI 移除。回傳 {"claude": bool, "codex": bool}。 (+21 more)

### Community 17 - "main.py"
Cohesion: 0.10
Nodes (24): _allowed_cors_origins(), cleanup_subprocesses(), handle_chat(), handle_chat_provider(), handle_session_rename(), handle_soul_reset(), handle_souls_list(), handle_team_chat() (+16 more)

### Community 19 - "safe_kill_process"
Cohesion: 0.09
Nodes (28): database._analyze_mcp_entry(), _load_local_mcp_cfg(), Read ~/.claude.json and return type + metadata for one MCP., _check_codex(), 已驗證：`codex login status` 已登入時輸出 "Logged in using ChatGPT"（純文字，     沒有 --json），e, Safely kill a process and its process tree, especially on Windows., Wrap command list on Windows if running a .cmd/.bat file to avoid WinError 193., safe_kill_process() (+20 more)

### Community 20 - "TestMemviewAPI"
Cohesion: 0.08
Nodes (14): GET /api/mem/system 應回傳內容, GET /api/mem/agents 應回傳 list（後端直接回傳陣列）, GET /api/mem/overview 應回傳結構化摘要, GET /api/mem/agents/{id} 應回傳該 agent 的記憶內容, PUT /api/mem/agents/{id} 應可以寫入, GET /api/mem/teams/{id} 應回傳該 team 的共享記憶, GET /api/mem/preview 應回傳預覽摘要, POST /api/team/chat 應能正常呼叫並回傳串流資料 (+6 more)

### Community 21 - "App Shell Component Template (app.html)"
Cohesion: 0.10
Nodes (26): ADR-002: Claude Codex Resource Sync, Agency Agents Importer, App Shell Component Template (app.html), Architect Agent (Soul Persona), Backend Runtime Requirements, backend-dev Docker Service, backend Docker Service (prod), claude-agent-sdk (Python dependency) (+18 more)

### Community 22 - "teams.py"
Cohesion: 0.15
Nodes (24): engines.availability.apply_availability_fallback() / NoEngineAvailableError, message_bus.global_bus (pub/sub for team:run_start/step_done/run_done), _agent_run_capture() — pluggable engine dispatch per agent, _claude_bin_and_key(), _diff_workspace_snapshot(), _execute_team_run() — timeout wrapper / circuit breaker, _execute_team_run_core() — parallel/sequential/consensus execution engine, _get_agent_memory_prompt() (+16 more)

### Community 23 - "MemoryAgent"
Cohesion: 0.12
Nodes (11): MemoryAgent, Path, Archival larger storage (Experience Projects + Project Internal logs), Build dynamic context with intelligent paging and RAG semantic similarity recall, path.stat() after an exists()/read_text() check is a TOCTOU race —         a co, Split text into smaller chunks for semantic retrieval, e.g., by headers or lines, Simple tokenizer and term frequency calculator with stop words filtering., Calculate cosine similarity between two term frequency mappings. (+3 more)

### Community 24 - "test_engine_registry.py"
Cohesion: 0.08
Nodes (17): 可插拔 agent engine（engines/ package）的測試。  背景：使用者要求把「執行任務的 CLI（Claude / Codex）」抽成, 2026-07-10：prompt 不再出現在指令列引數裡（見下方 stdin 測試的說明），     改成用 "-" 佔位、實際內容透過 stdin 傳，所, 2026-07-10 用真實 codex CLI 驗證發現：Windows 上 codex 是 npm .cmd     shim，wrap_cmd() 會包, 對照組：非 resume 的一般呼叫仍然要帶 --sandbox／--cd（只有 resume     子指令不接受這兩個 flag）。, 2026-07-10 用真實 codex CLI 驗證發現：CLI 層級的失敗（例如 resume     收到不支援的 flag）不會用 JSON 事件回報, 對照組：process 正常結束（returncode 0）但沒有任何輸出，不應該被     誤判成失敗——例如一個空的 turn。, 2026-07-11：用真實已登入帳號實測過 danger-full-access——這是目前     Windows 上唯一能讓 Codex 執行 Bash, 純文字附件（.txt/.md/.py/.ts/.js/.json，前端 accept 屬性允許的非圖片     格式）沒有對應的 CLI flag，直接讀內容 (+9 more)

### Community 25 - "TestIsSafeDockerIdent"
Cohesion: 0.08
Nodes (9): T2: 收斂 docker.sock 提權面 — CORS 不再對任意 origin 開 credentials， 且 /api/mcp-local-conf, 模擬舊版（無驗證）寫入的 config 檔仍殘留不安全值時，action 端點也要擋下。, 純函式測試，不需要 HTTP server, 驗證 CORS 中介層真的擋掉不在白名單內的來源（不只是檢查 helper 函式的回傳值）。, TestAllowedCorsOrigins, TestCorsEnforcement, TestIsSafeDockerIdent, TestMcpActionDefensiveValidation (+1 more)

### Community 26 - "register_team_routes"
Cohesion: 0.19
Nodes (23): /api/status route (backend health endpoint), engines.registry.ENGINES (registry of claude/codex engine impls), _team_dict(), _dirs(), gc_team_runs_cleanup_ctx(), handle_team_delete(), handle_team_get(), handle_team_post() (+15 more)

### Community 27 - "test_engine_mode_lockdown.py"
Cohesion: 0.16
Nodes (16): _FakeClaudeStdin, _FakeClaudeStdout, _make_fake_claude_subprocess(), 2026-07-12：Settings 新增可鎖定的「執行引擎範圍」（只用 Claude／只用 Codex／兩者都開放，database.get_engine, 對照組：mode='both' 時既有行為（agent 覆寫生效）要維持不變。, _read_sse_events(), _set_engine_mode(), test_agent_run_capture_locked_ignores_frontmatter_and_request() (+8 more)

### Community 29 - "test_hr_dispatch_execution_mode.py"
Cohesion: 0.13
Nodes (14): _FakeProc, _FakeStdout, _make_agents_dir(), 2026-07-10 team 協作優化健檢：HR Agent 自動組隊產生的 plan 從未帶 execution_mode 欄位，即使 routes/te, Model wraps the JSON in ```json fences AND forgets execution_mode —     both re, 2026-07-11：_run_hr_agent() 新增 engine_name 參數，讓 HR 派發本身     （挑選 Agent 組隊的那次文字補全）, 2026-07-11：resolve_key()（_resolve_api_key()）只解析 Anthropic key。     之前不分引擎一律傳給 e, 2026-07-13：反向驗證——Codex 引擎現在有自己的 resolver     （main._resolve_codex_api_key()），這裡 (+6 more)

### Community 30 - "apply_availability_fallback"
Cohesion: 0.13
Nodes (16): engines.availability.NoEngineAvailableError, apply_availability_fallback(), _bin_for(), _check_claude(), _format_notice(), engines.availability.get_status() (TTL cache), get_status() — engine availability TTL cache, NoEngineAvailableError (+8 more)

### Community 31 - "_load_config"
Cohesion: 0.16
Nodes (22): _load_config(), _log(), handle_config_get(), handle_debug_dump(), handle_line_webhook(), handle_schedules_parse_cron(), handle_translate(), _line_reply() (+14 more)

### Community 32 - "conftest.py"
Cohesion: 0.11
Nodes (17): Agent interface, Agent editor (openAgentEditor/saveAgentEditor), TestAgentCRUD (Agent CRUD API tests), TestMemoryCRUD (memory relay), TestMemviewAPI (/api/mem/*), app(), client(), _mock_engine_availability autouse fixture (+9 more)

### Community 33 - "MessageBus"
Cohesion: 0.13
Nodes (7): MessageBus, Any, Subscribe to a specific topic with a callback., Unsubscribe a callback from a topic., Publish a message to all subscribers of a topic asynchronously., bus(), T7: message_bus 的 async 訂閱者例外不應被靜默吃掉，且 create_task 需保留參照。

### Community 36 - "devDependencies"
Cohesion: 0.12
Nodes (17): @angular/build, @angular/cli, @angular/compiler-cli, devDependencies, @angular/build, @angular/cli, @angular/compiler-cli, jsdom (+9 more)

### Community 37 - "dependencies"
Cohesion: 0.12
Nodes (17): @angular/common, @angular/compiler, @angular/core, @angular/forms, @angular/platform-browser, @angular/router, dependencies, @angular/common (+9 more)

### Community 38 - "RunResult dataclass (engine turn result contract)"
Cohesion: 0.15
Nodes (15): MCP servers definition store (claude-desktop-mcp-servers.json), RunResult dataclass (engine turn result contract), ENGINES registry dict (name -> engine module), _read_skills_content() — inline skill content injector, _team_dict() — Team YAML -> dict builder, wrap_cmd() — Windows .cmd/.bat shim wrapper, find_claude()/find_codex() — CLI binary discovery, handle_chat() — single-agent chat SSE handler (+7 more)

### Community 40 - "engines.registry.resolve_engine_name_gated"
Cohesion: 0.27
Nodes (15): engines.availability.apply_availability_fallback(), helpers._agent_dict(), helpers._read_skills_content(), main.handle_chat (/api/chat), main.handle_team_chat (/api/team/chat), main.handle_team_execute (/api/team/execute), engines.registry.resolve_engine_name(), engines.registry.resolve_engine_name_gated() (+7 more)

### Community 41 - "TestAdversarialDebate"
Cohesion: 0.14
Nodes (13): HR Agent（總指揮）, Phase 2 — Teams 定義, Phase 3 — Multi-Agent 序列執行, Phase 4 — HR Agent（自動組隊）, Teams 系統, TestAdversarialDebate, _execute_team_run_core (routes/teams.py), test_consensus_with_four_members_produces_exactly_four_correct_steps (+5 more)

### Community 42 - "TestAgentCRUD"
Cohesion: 0.12
Nodes (4): ROADMAP Phase 1 — Agent CRUD（P1-B1 ~ P1-B3, P1-M1 ~ P1-M2）, sample_agent 是 session-scoped fixture，共用同一份 test-agent.md         物理檔案——同樣的理由見, 2026-07-11：Agent 編輯器 UI 加了引擎選擇下拉選單，engine 欄位要         能透過 PUT /api/agents/{id}, TestAgentCRUD

### Community 43 - "test_codex_api_key_and_bin_override.py"
Cohesion: 0.15
Nodes (6): 2026-07-13 續篇五：Settings 補齊 Codex 對等設定（執行路徑、API Key）。  涵蓋三件事： 1. `codex_engine, 兩個 resolver 完全分開讀各自的 config key，不會互相 fallback。, _set_config(), TestCodexApiKeyCmdConfigRoundTrip, TestCodexBinOverride, TestResolveCodexApiKey

### Community 44 - "TestTeamRunPathTraversalRejected"
Cohesion: 0.14
Nodes (6): 健檢第二輪：team run 相關修復 - wrap_cmd 在 routes/teams.py 從未被 import，導致每個 team run step, Regression test for wrap_cmd NameError: routes/teams.py previously never, TestIsSafeId, TestTeamRunPathTraversalRejected, TestWrapCmdFixedInTeamRun, _is_safe_id (routes/teams.py)

### Community 45 - "registry.py"
Cohesion: 0.21
Nodes (5): engines.registry.get_engine(), engines/registry.py — 引擎名稱 → 模組的對照表，以及「該用哪個引擎」的解析順序。  解析順序（優先序由高到低）： 1. Agent, resolve_engine_name(), 2026-07-13：使用者確認兩邊 CLI 都能用時，預設改成 Codex。, TestResolveEngineName

### Community 46 - "scripts"
Cohesion: 0.14
Nodes (14): scripts, backend:compile:linux, backend:compile:mac, backend:compile:win, build, build:linux, build:mac, build:win (+6 more)

### Community 47 - "test_backend.py"
Cohesion: 0.14
Nodes (5): 後端 API 整合測試 — 對應 ROADMAP.md 各 Phase 的核心端點  執行方式：     cd agent-desktop     py, ROADMAP 8.2 — Team 流水線完整性（不依賴 Claude CLI）, TestHealthCheck, TestSouls, TestTeamPipelineIntegrity

### Community 48 - "TestHelperFunctions"
Cohesion: 0.14
Nodes (4): ROADMAP Phase 1 — 工具函數測試（sync）, team.yaml 沒有 leader 欄位時，應自動 fallback 到第一個成員, team.yaml 有明確 leader 欄位時，應使用指定的 leader, TestHelperFunctions

### Community 49 - "test_mcp_sync.py"
Cohesion: 0.15
Nodes (7): 2026-07-11：MCP server 定義同步到 Claude／Codex 兩邊 CLI 的核心邏輯 （backend/mcp_sync.py）。這裡驗, 驗證 _sync_lock 真的序列化了呼叫——用一個會記錄進入/離開順序的假     _run_cli，確認同時發起的兩次 sync_add 不會交錯執行。, 已確認：Codex 的 HTTP MCP 沒有任意 header 機制（只有     --bearer-token-env-var／OAuth），header, _run_cli 本身遇到 FileNotFoundError（binary 不存在）要吞掉、回傳 False，     不能讓整個 sync_add 拋例外, test_codex_add_args_http_ignores_headers(), test_sync_add_cli_not_found_returns_false_not_exception(), test_sync_operations_are_serialized_by_lock()

### Community 50 - "run_import"
Cohesion: 0.24
Nodes (11): fetch_json(), fetch_text(), get_claude_home(), agency_agents_importer._is_safe_id(), Path, div_key 會被拿去拼 team_id/team_file 檔名（見下方 run_import）。這個值     來自釘死版本的上游 GitHub rep, run_import(), importAgencyAgents() -> POST /api/agents/import-agency (+3 more)

### Community 51 - "database.get_engine_mode"
Cohesion: 0.20
Nodes (11): database.get_engine_mode(), 權威值，決定 agent 自己的 engine: frontmatter 覆寫在執行期是否生效：     'claude'/'codex' 表示鎖定單一引擎（, AppSettings interface, engineMode config round-trip tests, _build_full_prompt, build_team_memory_context, handle_team_chat (main.py), test_first_turn_team_chat_does_not_raise_nameerror (+3 more)

### Community 52 - "engines.codex_engine.run_turn"
Cohesion: 0.26
Nodes (10): engines.codex_engine._codex_bin(), _inject_text_attachments(), _normalize_sandbox_mode(), engines/codex_engine.py — OpenAI Codex CLI 的 AgentEngine 實作。  2026-07-10／07-11, 把附件路徑分成「圖片」（走 -i flag）跟「純文字」（讀內容折進 prompt）     兩類。已驗證 codex exec 跟 codex exec r, engines.codex_engine.run_turn(), _split_attachments(), main() (CLI diagnostic entrypoint) (+2 more)

### Community 53 - "handle_schedules_post"
Cohesion: 0.29
Nodes (10): handle_schedules_delete(), handle_schedules_get(), handle_schedules_patch(), handle_schedules_post(), handle_schedules_run(), load_schedules(), _natural_to_cron(), Check every 60 s whether any enabled schedule is due to run. (+2 more)

### Community 54 - "_resolve_agent_engine_and_key"
Cohesion: 0.24
Nodes (11): get_engine_mode(), get_engine(), resolve_engine_name_gated(), _agent_dict() — Agent frontmatter -> dict builder, 比照 routes/teams.py::_agent_run_capture() 已經驗證過的模式：讀     agent 自己 frontmatter 宣告, 跟 _resolve_api_key() 幾乎一樣，只是讀 codexApiKeyCmd 這個獨立的     config key、回傳的值只會被拿去設 CO, _resolve_agent_engine_and_key(), main._resolve_codex_api_key() (+3 more)

### Community 55 - "package.json"
Cohesion: 0.18
Nodes (10): electron-builder, electron-updater, dependencies, electron-updater, description, devDependencies, electron-builder, main (+2 more)

### Community 57 - "_agent_run_capture (routes/teams.py)"
Cohesion: 0.24
Nodes (11): _agent_run_capture (routes/teams.py), test_agent_run_capture_calls_wrap_cmd_without_nameerror, wrap_cmd (missing import regression in routes/teams.py), engines.claude_engine.run_turn, engines.codex_engine.run_turn, engines.registry.resolve_engine_name, main._resolve_api_key (Anthropic key resolver), main._resolve_codex_api_key (+3 more)

### Community 58 - "build_team_memory_context"
Cohesion: 0.27
Nodes (10): _encode_slug(), Convert a filesystem path to the Claude Code project slug format., build_memory_context(), build_team_memory_context(), handle_mem_preview(), Debug 端點：預覽 build_memory_context / build_team_memory_context 的輸出。     GET /api/, 使用 MemoryAgent 進行動態分層加載與智能 Context 裁剪與 RAG 召回。, 組裝 Team Run 的記憶 context。     使用 MemoryAgent 來對當前成員的 Identity 與 Project 內部日誌進行智能 (+2 more)

### Community 59 - "engines.registry.resolve_engine_name_gated"
Cohesion: 0.29
Nodes (5): 疊加在 resolve_engine_name() 之上的「模式鎖定」層。mode 是     database.get_engine_mode() 的回傳值, engines.registry.resolve_engine_name_gated(), 跟 TestResolveEngineName 用同一組案例，證明 mode='both' 是真正的         pass-through，不是巧合地算出, get_engine_mode() 自己已經正規化過，理論上不會把非法值傳進來，但         這個函式本身也要 fail safe——未知 mode 值, TestResolveEngineNameGated

### Community 60 - "files"
Cohesion: 0.20
Nodes (9): electron, { contextBridge, ipcRenderer }, files, electron, backend/claude-backend, backend/claude-backend.exe, backend/presets/**/*, frontend/dist/**/* (+1 more)

### Community 62 - "TestHRAgent"
Cohesion: 0.20
Nodes (6): ROADMAP Phase 4 — P4-B1 ~ P4-B3, GET /api/agents/registry 應回傳帶有 description 與 skills 的列表, 如果 agents 目錄下沒有 .md 檔，回傳空列表, POST /api/hr/dispatch 不帶 task 應回傳 400, 沒有任何 agent 時 HR dispatch 應回傳錯誤（不需要呼叫 Claude CLI）, TestHRAgent

### Community 63 - "test_line_webhook_auth.py"
Cohesion: 0.24
Nodes (4): T31: LINE webhook 簽章驗證原本在 lineChannelSecret 未設定時直接放行 （fail-open）——設定到一半的期間，任何人都, _sign(), TestLineWebhookEndpointFailsClosed, TestVerifyLineSignatureFailsClosed

### Community 64 - "TestRestoreZipBomb"
Cohesion: 0.38
Nodes (5): _make_zip(), _post_restore(), T30: handle_restore 用 zf.read() 把整個 zip 項目解壓進記憶體，原本沒有 任何大小檢查。上傳的 zip 本身雖受 clien, TestRestoreZipBomb, handle_restore (/api/restore zip-bomb guard)

### Community 65 - "_FakeStdout"
Cohesion: 0.22
Nodes (3): _FakeProc, _FakeStdout, 2026-07-10 team 協作優化健檢：handle_team_chat() 的 _build_full_prompt() 呼叫 build_team_

### Community 66 - "_FakeStdout"
Cohesion: 0.22
Nodes (3): _FakeProc, _FakeStdout, 2026-07-10 team 協作優化健檢：發現 7 — 團隊對話組長的回覆文字裡只要出現 `[APPROVE: <request_id>]`，系統就會直接

### Community 67 - "test_upgrade.py"
Cohesion: 0.22
Nodes (6): TestMcpDebugger, TestMessageBus, TestSensitiveToolGatekeeper, _analyze_mcp_entry (routes/mcp_debugger.py), global_bus (message_bus.py), handle_mcp_rpc (routes/mcp_debugger.py)

### Community 68 - "TestTeamFailsafe"
Cohesion: 0.20
Nodes (6): TestTeamFailsafe, _kill_team_run_processes (routes/teams.py), _register_team_proc (routes/teams.py), safe_kill_process (process-kill utility), _team_run_processes (dict[run_id -> set[proc]]), _unregister_team_proc (routes/teams.py)

### Community 69 - "engines.claude_engine.run_turn"
Cohesion: 0.25
Nodes (8): _claude_bin(), engines/claude_engine.py — Claude Code CLI 的 AgentEngine 實作。  這是 routes/teams., engines.claude_engine.run_turn(), engines.base.RunResult, test_handle_team_chat_engine_routing.py - handle_team_chat engine routing test suite, test_handle_team_execute_engine_routing.py - handle_team_execute engine routing test suite, test_hr_dispatch_execution_mode.py - _run_hr_agent execution_mode test suite, test_team_run_execution_mode.py (referenced, execution_mode propagation test)

### Community 70 - "handle_mcp_rpc"
Cohesion: 0.31
Nodes (8): _cleanup_pending_auth(), _consume_pending_auth(), handle_mcp_rpc(), _is_safe_name(), Sensitive Tool Gatekeeper (_PENDING_AUTH / cleanup / consume), Request, Response, 驗證並消耗一次 pending 授權。必須是伺服器先前核發、且對應同一筆請求內容。

### Community 71 - "scripts"
Cohesion: 0.22
Nodes (9): scripts, build, e2e, e2e:report, e2e:ui, ng, start, test (+1 more)

### Community 72 - "build"
Cohesion: 0.22
Nodes (9): build, appId, asar, directories, productName, win, output, icon (+1 more)

### Community 73 - "TestTeamRun"
Cohesion: 0.22
Nodes (3): ROADMAP Phase 3 — P3-B1 ~ P3-B5, 使用 team payload 而非 team_id，驗證 run_id 生成, TestTeamRun

### Community 74 - "test_database.py"
Cohesion: 0.22
Nodes (5): T9: database.py 的 _init_db 自我修復邏輯不應對任何 sqlite3.Error 都刪除重建索引 DB， 只有真的偵測到檔案損毀時才重, A locked/busy DB (OperationalError) must propagate, not trigger deletion of, _db() must not leak an open handle when PRAGMA setup fails on a corrupted file, test_db_connection_closed_when_setup_fails(), test_transient_operational_error_is_not_swallowed()

### Community 75 - "TestSessionSnippetEscaping"
Cohesion: 0.31
Nodes (5): T44: session 搜尋回傳的 snippet 會經前端 [innerHTML] 直接渲染（略過 markdown pipe 的 DOMPurify），, 短查詢（<3 字元）走 LIKE fallback，且會把查詢字串本身包進 <mark> —         這裡驗證『使用者自己在搜尋框打的字』也會被跳脫（, TestSessionSnippetEscaping, _write_session_file(), GET /api/sessions (FTS5 snippet + LIKE fallback)

### Community 76 - "_PersistentSessions"
Cohesion: 0.39
Nodes (3): handle_chat_clear(), _PersistentSessions, dict

### Community 77 - "TestSessionAdvanced"
Cohesion: 0.25
Nodes (5): Session rename、messages 查詢端點, 不存在 session 的 messages 查詢應優雅回應（不 crash）, 對不存在的 session 做 rename 應優雅回應（不 crash 成 500）, 對不存在的 session 做 auto-title 應優雅回應, TestSessionAdvanced

### Community 79 - "FakeService"
Cohesion: 0.36
Nodes (4): FakeService, test_resource_sync_dry_run(), test_resource_sync_rejects_non_boolean_dry_run(), test_resource_sync_status()

### Community 80 - "handle_run_artifacts"
Cohesion: 0.33
Nodes (5): handle_run_artifacts(), _is_safe_id(), Request, Response, SSE_BODY

### Community 82 - "TestMemoryCRUD"
Cohesion: 0.29
Nodes (3): ROADMAP Phase 1 — Memory 讀寫，及 Phase 3.C Memory Relay, Phase 3.C：Memory 中繼驗證 — 寫入後可讀回相同內容, TestMemoryCRUD

### Community 84 - "TestSchedulePatch"
Cohesion: 0.29
Nodes (4): PATCH /api/schedules/{id} — 啟用/停用排程, 建立排程 → PATCH 停用 → 確認 enabled=False, 對不存在的 schedule ID 執行 run 應回傳 404, TestSchedulePatch

### Community 86 - "test_team_run_execution_mode.py"
Cohesion: 0.29
Nodes (5): 2026-07-10 team 協作優化健檢：execution_mode 對 inline team payload 失效。  _execute_team, Explicit regression guard: absence of execution_mode must still default     to, POST /api/team/run must persist the inline payload's execution_mode     into ru, test_handle_team_run_post_stores_inline_execution_mode(), test_inline_payload_without_execution_mode_still_defaults_parallel()

### Community 87 - "test_team_run_process_tracking.py"
Cohesion: 0.48
Nodes (6): FakeProc, T23: parallel 模式下同一個 run_id 底下多個 step 各自 spawn 一個 process， 原本用單一 dict[run_id]=p, test_kill_team_run_processes_kills_every_tracked_proc(), test_last_unregister_cleans_up_empty_entry(), test_register_multiple_procs_same_run_id_tracked_independently(), test_unregister_one_does_not_drop_the_others()

### Community 88 - "_CustomModule — dynamic cross-instance database state sync pattern"
Cohesion: 0.33
Nodes (5): run_import() — Agency Agents Catalog Importer, database.py config/state module (CLAUDE_HOME, AGENTS_DIR, SKILLS_DIR, TEAMS_DIR, SOULS_DIR), _CustomModule — dynamic cross-instance database state sync pattern, handle_agent_import_agency() route handler, routes/__init__.py route registration aggregator

### Community 89 - "api getter (same-origin vs Electron port fallback)"
Cohesion: 0.33
Nodes (6): api getter (same-origin vs Electron port fallback), backend:compile:* PyInstaller scripts, electron-builder app config (agent-desktop), Dev Proxy /api -> localhost:8765, DEFAULTS AppSettings object (backendPort 8765), start.sh launcher (dev/docker/prod modes)

### Community 90 - "nsis"
Cohesion: 0.33
Nodes (6): nsis, allowToChangeInstallationDirectory, createDesktopShortcut, createStartMenuShortcut, oneClick, shortcutName

### Community 94 - "test_db_ctx.py - _db_ctx() context manager test suite"
Cohesion: 0.50
Nodes (4): database._db(), database._init_db(), test_database.py - _init_db self-healing test suite, test_db_ctx.py - _db_ctx() context manager test suite

### Community 95 - "frontend/package.json (scripts: start/build/test/e2e)"
Cohesion: 0.40
Nodes (4): angular.json (build/serve/test architect config, proxy.conf.json), frontend/package.json (scripts: start/build/test/e2e), .vscode/launch.json (ng serve / ng test debug configs), .vscode/tasks.json (npm start/test background tasks)

### Community 96 - "package.json"
Cohesion: 0.40
Nodes (4): name, packageManager, private, version

### Community 97 - "Researcher Agent (Soul Persona)"
Cohesion: 0.40
Nodes (5): Researcher Agent (Soul Persona), Research Translation Team, Text Translator Skill, Translator Agent (Soul Persona), Web Scraper Skill

### Community 98 - "TestSoulAdvanced"
Cohesion: 0.40
Nodes (3): Soul rename / delete 端點測試, Soul rename 端點（POST /api/souls/{id}/rename）, TestSoulAdvanced

### Community 100 - "test_team_run_error_handling.py"
Cohesion: 0.40
Nodes (3): 2026-07-10 team 協作優化健檢：_execute_team_run() 原本用 `except Exception: pass` 把 _exec, Without _finished_at, _cleanup_old_runs() can never evict a crashed     run — i, test_core_exception_run_is_now_eligible_for_gc()

### Community 102 - "_cleanup_old_runs"
Cohesion: 0.50
Nodes (4): _cleanup_old_runs(), _gc_team_runs_task(), Remove finished runs older than max_age seconds (default 2 h)., Background task to cleanup old team runs, preventing leaks.

### Community 103 - "Team Run UI logic (_dispatchTeamRun/_applyTeamRunEvent)"
Cohesion: 0.50
Nodes (4): streamTeamRun() SSE fetch method, TeamRun/TeamRunStep interfaces, Team Run UI logic (_dispatchTeamRun/_applyTeamRunEvent), TestTeamRun / TestTeamPipelineIntegrity

### Community 105 - "test_mcp_docker_hardening.py - Docker MCP security hardening test suite"
Cohesion: 0.67
Nodes (3): main._is_safe_docker_ident(), main /api/mcp-local-config/{name} and /api/mcp/{name}/{action} routes, test_mcp_docker_hardening.py - Docker MCP security hardening test suite

### Community 106 - "linux"
Cohesion: 0.50
Nodes (4): linux, category, icon, target

### Community 107 - "mac"
Cohesion: 0.50
Nodes (4): mac, category, icon, target

### Community 108 - "publish"
Cohesion: 0.50
Nodes (4): publish, owner, provider, repo

### Community 109 - "test_resource_sync_routes.py - /api/resource-sync route test suite"
Cohesion: 0.67
Nodes (4): resource_sync.ResourceSyncService, routes.resource_sync._service() / /api/resource-sync route, test_resource_sync_routes.py - /api/resource-sync route test suite, test_resource_sync.py - ResourceSyncService test suite

### Community 112 - "test_memory_agent_toctou.py"
Cohesion: 0.50
Nodes (3): T32: MemoryAgent.get_archival_memory() 原本在 exists()/read_text() 檢查 後又對同一個檔案呼叫 s, test_get_archival_memory_survives_vanishing_project_file(), test_safe_mtime_falls_back_when_file_vanishes()

## Ambiguous Edges - Review These
- `agency_agents_importer._is_safe_id()` → `importAgencyAgents() -> POST /api/agents/import-agency`  [AMBIGUOUS]
  frontend/src/app/claude.service.ts · relation: conceptually_related_to
- `database._analyze_mcp_entry()` → `_is_safe_mcp_name()`  [AMBIGUOUS]
  backend/routes/mcp_servers.py · relation: conceptually_related_to
- `_agent_run_capture() — pluggable engine dispatch per agent` → `SessionPool class — pooled ClaudeSDKClient connections`  [AMBIGUOUS]
  backend/session_pool.py · relation: conceptually_related_to
- `SessionPool class — pooled ClaudeSDKClient connections` → `handle_chat() — single-agent chat SSE handler`  [AMBIGUOUS]
  backend/main.py · relation: shares_data_with
- `claude_engine.run_turn() — Claude CLI subprocess driver` → `handle_chat() — single-agent chat SSE handler`  [AMBIGUOUS]
  backend/main.py · relation: calls
- `codex_engine.run_turn() — Codex CLI subprocess driver` → `handle_chat() — single-agent chat SSE handler`  [AMBIGUOUS]
  backend/main.py · relation: calls
- `codex_engine.run_turn() — Codex CLI subprocess driver` → `handle_team_chat() — multi-agent discussion loop`  [AMBIGUOUS]
  backend/main.py · relation: calls
- `App root component` → `secureStorage encrypted providerApiKey handling`  [AMBIGUOUS]
  frontend/src/app/settings.service.ts · relation: conceptually_related_to
- `SKILL_MCPS_MAP hardcoded skill->MCP mapping` → `skill-content-into-prompt injection tests`  [AMBIGUOUS]
  tests/test_agent_run_capture_skills.py · relation: conceptually_related_to
- `handle_team_run_post (routes/teams.py, POST /api/team/run)` → `test_agent_run_capture_defaults_to_accept_edits`  [AMBIGUOUS]
  tests/test_team_run_permission_mode.py · relation: conceptually_related_to
- `MemoryAgent (memory_agent.py)` → `global_bus (message_bus.py)`  [AMBIGUOUS]
  tests/test_upgrade.py · relation: conceptually_related_to
- `Dev Architect Team` → `Agency Agents Importer`  [AMBIGUOUS]
  frontend/src/app/app.html · relation: conceptually_related_to
- `Backend Build Requirements (PyInstaller)` → `backend Docker Service (prod)`  [AMBIGUOUS]
  backend/requirements-build.txt · relation: conceptually_related_to

## Knowledge Gaps
- **232 isolated node(s):** `docker-entrypoint.sh script`, `{ app, BrowserWindow, shell, Tray, Menu, nativeImage, dialog, ipcMain, Notification, safeStorage }`, `path`, `fs`, `{ spawn, execFileSync }` (+227 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **51 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `agency_agents_importer._is_safe_id()` and `importAgencyAgents() -> POST /api/agents/import-agency`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `database._analyze_mcp_entry()` and `_is_safe_mcp_name()`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `_agent_run_capture() — pluggable engine dispatch per agent` and `SessionPool class — pooled ClaudeSDKClient connections`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `SessionPool class — pooled ClaudeSDKClient connections` and `handle_chat() — single-agent chat SSE handler`?**
  _Edge tagged AMBIGUOUS (relation: shares_data_with) - confidence is low._
- **What is the exact relationship between `claude_engine.run_turn() — Claude CLI subprocess driver` and `handle_chat() — single-agent chat SSE handler`?**
  _Edge tagged AMBIGUOUS (relation: calls) - confidence is low._
- **What is the exact relationship between `codex_engine.run_turn() — Codex CLI subprocess driver` and `handle_chat() — single-agent chat SSE handler`?**
  _Edge tagged AMBIGUOUS (relation: calls) - confidence is low._
- **What is the exact relationship between `codex_engine.run_turn() — Codex CLI subprocess driver` and `handle_team_chat() — multi-agent discussion loop`?**
  _Edge tagged AMBIGUOUS (relation: calls) - confidence is low._