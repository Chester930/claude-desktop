# Claude 桌面版 — 計畫任務書（進版交接用）

> **快照時間**：2026-07-02 15:28 (UTC+8)
> **當前分支**：`master` @ [1226962](file:///c:/Users/mycena/claude-desktop)
> **用途**：換機續做用的完整進度記錄

---

## 一、專案概述

**Claude 桌面版** 是 Claude Code CLI 的 Electron 圖形介面，支援多面板對話、Agent/Skill/MCP 管理、Team 多代理人協作、排程、LINE Bot 等功能。

| 層級 | 技術 |
|------|------|
| Frontend | Angular 22 + SCSS |
| Backend | Python 3.10+ / aiohttp |
| Desktop | Electron 42 |
| 容器化 | Docker Compose |

---

## 二、已完成工作總覽

### 2.1 近兩日 commits（7/1 ~ 7/2，共 16 筆）

| Commit | 類別 | 說明 |
|--------|------|------|
| `1226962` | **feat** | ⭐ **Part A：persistent claude-agent-sdk connections for team chat** — 在 `handle_team_chat` 中引入 `session_pool.py`，改為長駐 SDK 連線，不再每次重新 spawn `claude -p` 子程序 |
| `c1cc24d` | feat(ui) | Team 編輯器加入 `execution_mode` 欄位（sequential / parallel） |
| `ae1e2b9` | feat(team) | `active_sessions` 新增過期清除機制 |
| `4ecd2ff` | fix(team) | Windows Terminal monitor 只在原生 Windows 啟動 |
| `e5d85bb` | perf | 移除 soul-sync 的死代碼副作用，檔案讀取改為並行 |
| `ea26eca` | fix(team) | 過濾掉 claude CLI 的診斷雜訊（影響 inter-agent context） |
| `cc512a1` | fix(team) | `execution_mode` 從未被讀取導致 sequential 模式失效 |
| `d44cfd3` | feat(ui) | Skill 編輯器的 description 改為可編輯 + 自動換行 |
| `6f615c5` | feat(ui) | Agent 編輯器新增 description textarea |
| `f2315e9` | fix(ui) | Team 編輯器 description 欄位自動換行 |
| `bf595bc` | feat(soul) | 恢復 4 個手寫 preset agents 的原始 souls |
| `52314f2` | fix(soul) | Soul 改為 1:1 對應 Agent（不再全域串接） |
| `5d77b46` | fix(team) | 持久化 `active_sessions`，阻止無限制 context 累積 |
| `d489a30` | merge | 合併遠端 master |
| `53a7598` | feat | 後端 session 管理 + 排程 + multi-layer memory context builder |
| `14be0c1` | feat | Claude service + 前端 team/session 管理基礎架構 |

### 2.2 Part A — Session Pool 遷移（最重要的架構改動）

**目標**：把 Team Chat 的每次對話從「spawn 新 `claude -p` 子程序 → --resume 重建 context」改為「複用長駐 SDK 連線」。

**已完成的遷移點**：
- ✅ `handle_team_chat` → `run_single_agent` 已改為使用 `SessionPool`
- ✅ 新增 [session_pool.py](file:///c:/Users/mycena/claude-desktop/backend/session_pool.py)（30 分鐘 idle evict、key-based 連線池）
- ✅ fallback 機制：SDK 不可用或出錯時，退回 legacy 子程序模式
- ✅ `GET /api/status` 新增 `pool_size` 欄位供外部驗證
- ✅ 實測驗證：同一 client_id 的重複 request 不會增長 pool size

**尚未遷移的兩個點**（Part A 後續）：
- ❌ `handle_chat`（單一 Agent 對話主路徑）— 風險較高
- ❌ `handle_team_execute`（工具使用 + 互動式權限核准）— 涉及 `can_use_tool` callback

### 2.3 Part B — Agent Teams 調查結論

> [!IMPORTANT]
> **重大發現**：`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 在 `-p` 非互動模式下 **不會** 觸發 Agent Teams。`~/.claude/teams/` 底下沒有產生新的 session 目錄。結論：**Agent Teams 目前無法透過 headless 架構驅動**。

---

## 三、未提交的變更（⚠️ 換機前必須處理）

> [!CAUTION]
> 目前有 **2 個檔案已修改但未 commit**，換機前務必 commit 或 stash push 後 push 到 remote。

```
modified:   backend/main.py          (560 行差異：+369 / -194)
modified:   backend/session_pool.py  (+3 行：新增 keys() 方法)
```

### 未提交變更的內容摘要

#### [main.py](file:///c:/Users/mycena/claude-desktop/backend/main.py) — `handle_team_execute` 遷移到 pooled 模式

這是 **Part A 的第三個遷移點**（`handle_team_execute`），主要改動：

1. **新增 `_pooled_exec()` 內部函式**：透過 `session_pool` 送出 query，重用長駐連線
2. **`can_use_tool` callback 實作**：權限核准改為透過 `PermissionResultAllow` / `PermissionResultDeny` 而非 subprocess stdin 寫入
3. **串流輸出**：pooled 模式下以 `AssistantMessage` / `TextBlock` / `ResultMessage` 接收 SSE 事件
4. **fallback 路徑**：pooled 失敗時 evict 並退回 `_legacy_exec`
5. **stop 路由加入 pool evict**：`handle_chat_stop` 新增清除相關 pool key 的邏輯

#### [session_pool.py](file:///c:/Users/mycena/claude-desktop/backend/session_pool.py) — 新增 `keys()` 方法

```python
def keys(self) -> list[str]:
    return list(self._clients.keys())
```

> [!WARNING]
> 這些變更尚未經過實測（因為 hit session limit）。換機後首要任務是驗證此遷移。

---

## 四、換機操作步驟

### 4.1 在舊電腦上（離開前做）

```bash
cd claude-desktop

# 方案 A：直接 commit（推薦）
git add backend/main.py backend/session_pool.py
git commit -m "wip(team): migrate handle_team_execute to pooled SDK connections (untested)"
git push origin master

# 方案 B：stash 推送（如果不想留 WIP commit）
git stash push -m "Part A: handle_team_execute pooled migration (untested)"
# stash 無法 push 到 remote，需改用 commit 方式
```

### 4.2 在新電腦上

```bash
git clone https://github.com/Chester930/claude-desktop.git
cd claude-desktop

# 安裝依賴
pip install -r backend/requirements.txt
cd frontend && npm install && npm run build && cd ..
npm install

# 如果用了 stash（不推薦）
# git stash pop
```

---

## 五、接續開發計畫

### 🔴 P0 — 立即要做（Part A 收尾）

- [ ] **驗證 `handle_team_execute` 的 pooled 遷移**（未提交的 main.py 變更）
  - 啟動 Team → 觸發工具使用 → 確認 `can_use_tool` callback 正確收到權限請求
  - 確認 SSE 串流輸出正常
  - 確認 fallback 路徑可用
  - 確認 `handle_chat_stop` 的 pool evict 有效

- [ ] **遷移 `handle_chat`**（Part A 第二個遷移點）
  - 這是單一 Agent 的主對話路徑，風險最高
  - 需要處理：file attachments、system prompt injection、streaming
  - 建議策略：先 pooled，失敗退回 legacy

### 🟡 P1 — 短期（ROADMAP Phase 1 — Agent Mapping）

Phase 1 共 24 個項目，全部 `[ ]` 尚未開始，詳見 [ROADMAP.md](file:///c:/Users/mycena/claude-desktop/ROADMAP.md) 第 221-309 行。

重點項目：
- [ ] P1-B1：解析 agent frontmatter 的 `skills / memory / mcp / soul / output_memory`
- [ ] P1-F2：「啟動 Agent」按鈕的一鍵切換行為
- [ ] P1-M3~M8：Agent 編輯器 Modal

### 🟢 P2 — 中期（Phase 2-3 — Teams + Multi-Agent 執行）

- [ ] P2：Teams UI 管理（CRUD、拖曳排序）
- [ ] P3：Multi-Agent 序列流水線（後端子程序管理 + 任務狀態 DB）

### 🔵 P3 — 長期（Phase 4 — HR Agent 自動組隊）

- [ ] P4：HR Agent orchestrator + 動態 Team 組建

---

## 六、已知問題與技術債

| # | 類別 | 問題 | 備註 |
|---|------|------|------|
| 1 | 架構 | `main.py` 已達 4216 行 / 176KB | 急需拆分模組（routes、services、models） |
| 2 | 限制 | Agent Teams 無法 headless 驅動 | Part B 結論，需等 Anthropic 支援或找替代方案 |
| 3 | 測試 | `handle_team_execute` pooled 遷移未經實測 | 換機後第一優先 |
| 4 | 依賴 | `claude-agent-sdk` 為選用依賴 | 需要 fallback 測試覆蓋 |
| 5 | UI | Agent/Skill/Team 編輯器已有 description 欄位，但 frontmatter 解析尚未完整 | Phase 1 範圍 |

---

## 七、專案檔案結構速查

```
claude-desktop/
├── electron/              # Electron 主程序 + preload
├── frontend/              # Angular 22 前端
│   └── src/app/
│       ├── app.ts         # 主元件
│       ├── app.html       # 模板
│       ├── app.scss       # 深色主題樣式
│       ├── claude.service.ts  # API client
│       └── markdown.pipe.ts   # Markdown 渲染 pipe
├── backend/
│   ├── main.py            # ⚠️ 所有 API routes（4216 行，待拆分）
│   ├── session_pool.py    # SDK 連線池（Part A 新增）
│   ├── database.py        # SQLite + FTS5
│   ├── watcher.py         # 檔案變更監控
│   └── presets/           # 預設 agents/skills/souls
├── tests/                 # Pytest 測試
├── ROADMAP.md             # Phase 1-4 路線圖（48 項目）
├── docker-compose.yml     # Docker 服務編排
├── start.bat / start.sh   # 一鍵啟動腳本
└── .claude/               # Claude Code 工作區設定
```

---

## 八、開發環境需求

| 工具 | 版本 | 備註 |
|------|------|------|
| Node.js | ≥ 22.22.3 | 前端建置 + Electron |
| Python | ≥ 3.10 | 後端 |
| Claude CLI | 最新版 | `npm i -g @anthropic-ai/claude-code` |
| claude-agent-sdk | 最新版 | `pip install claude-agent-sdk`（選用，Part A 需要） |
| Docker Desktop | 最新版 | 測試 LINE Bot 時需要 |

---

> [!TIP]
> **快速恢復開發**：clone → 安裝依賴 → `.\start.bat --dev` → 驗證 pooled migration → 繼續 Phase 1。
