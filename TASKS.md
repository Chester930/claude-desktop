# Claude 桌面版 功能任務書
更新：2026-06-24

優先度 = 重要性 × 容易程度

---

## P1 快速完成（簡單 + 高頻使用）

- [x] **T01** 輸入列底部狀態列 — 模型 / 思考深度 / 權限模式 selector（對標官方 Claude Desktop）
- [x] **T02** Select folder 按鈕 — 原生資料夾選擇器（Electron dialog IPC + preload.js）
- [x] **T03** Ctrl+V 截圖貼上 — 剪貼簿圖片直接送進對話（HostListener paste）
- [x] **T04** 拖曳檔案進對話框 — drag & drop 上傳（dragover/drop/dragleave）
- [x] **T05** 任務完成 Windows 通知 — 串流結束後發 toast（Electron Notification IPC）
- [x] **T06** 工具執行計時器 — tool call 旁顯示已花幾秒（toolTick signal + interval）

## P2 中等工程量（有明顯收益）

- [x] **T07** 首頁 Dashboard — 統計卡片（sessions / messages / tokens / streak）+ 活動熱點圖（heatmap）
- [x] **T08** --continue 按鈕 — 側欄「⏎ 繼續上次」按鈕（取最新 session resume）
- [x] **T09** claude doctor 診斷頁 — 執行 `claude doctor`/`update` 並顯示輸出（設定頁）
- [x] **T10** MCP 管理頁 — `claude mcp list` 顯示 + 右側面板 MCP tab

## P3 複雜功能（大工程，分批做）

- [x] **T11** 對話畫布 — 最多 4 個面板並排；sidebar session 拖入畫布新增面板
- [x] **T12** 面板調整大小 — 欄 / 列之間有拖曳把手，即時調整比例
- [x] **T13** 移除 file tree — 已由 sidebar 拖曳取代
- [x] **T14** ⌘K 全局搜尋 — Ctrl+K，搜指令/對話/代理人/技能

---
*每完成一項自動更新此檔案*
