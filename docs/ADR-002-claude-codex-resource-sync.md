# ADR-002：Claude Code 與 Codex 資源同步

## 狀態

已採用（2026-07-13）

## 背景

Agent Desktop 同時支援 Claude Code CLI 與 Codex CLI。面板原本直接讀寫
`~/.claude/agents`、`~/.claude/skills`，所以與 Claude Code 共用同一份資料；
但 Codex 的原生 Agent 使用 TOML，Skill 也位於不同根目錄。MCP 已透過兩邊
CLI 的 `mcp add`／`mcp remove` 同步。

## 決策

1. `claudeHome` 是 Agent Desktop 的 Agent／Skill 單一來源，與 Claude Code
   直接共用，不建立桌面板私有副本。
2. Agent Desktop 將 Claude Markdown Agent 轉成 Codex TOML，部署至
   `~/.codex/agents`。
3. Skill 使用相同 `SKILL.md` 內容；部署至 `~/.agents/skills/<name>`。執行
   同步時複製完整目錄，保留 references、scripts、assets。
4. 只更新帶有 Agent Desktop 管理標記的副本；同名非受管內容不同時列為
   conflict，絕不靜默覆蓋。
5. 狀態檢查只比較 Agent 定義與 Skill 入口檔，避免讀取數百個 Skill 的所有
   大型資產；真正同步時才複製完整 Skill 目錄。
6. 同步不自動刪除 Codex-only 資源。

## 結果

### 優點

- Claude Code 與桌面板零複製、即時共用。
- Codex 可取得原生 Agent／Skill，不依賴提示詞注入才能看見資源。
- 預覽與衝突保護降低批次覆蓋使用者設定的風險。
- MCP 繼續由官方 CLI 寫入設定，不直接處理可能含憑證的設定檔。

### 代價

- Agent 因格式不同必須產生 Codex 副本，並非真正的同一個檔案。
- 狀態比較以 Skill 入口檔為主；只有 references/assets 改變而入口不變時，
  不會自動判定為過期。
- 目前同步方向以 Claude／Agent Desktop 為主來源；Codex-only 資源保留但不
  自動反向轉換。

## 未採用方案

- **Windows junction／symbolic link**：既有目錄已包含大量不同資源，合併與
  權限行為不穩定，且 Agent 格式仍不相容。
- **直接改寫 Claude/Codex MCP 設定檔**：設定可能包含 token，且格式會隨 CLI
  版本改變；沿用 CLI 指令較安全。
- **遇到同名即覆蓋**：會破壞使用者自行維護的 Codex Agent／Skill，因此拒絕。
