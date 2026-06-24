# 專案開發進度與接續指南 (Claude Desktop 視覺化面板)

本文件紀錄了目前 Claude Desktop 視覺化面板的前端重構進度，以便您在之後接續進行開發。

---

## 📌 目前進度摘要
我們正在將右側面板中**代理人 (Agents)** 與**技能 (Skills)** 卡片的「翻譯按鈕」與「行內簡介」移除，改為以**「查看詳情」彈窗 (Detail Modal)** 呈現。

1. **已修改的組件邏輯 (`app.ts`)**：
   - 新增了 `detailItem` 信號，用於記錄當前打開詳情的項目資訊（包含：`id`、`label`、`name`、`description`、`type`）。
   - 新增了 `detailTranslation` 信號，記錄翻譯後的文字狀態（`null` 為未翻譯、`''` 為載入中）。
   - 實現了以下控制方法：
     - `openDetail(item)`: 開啟詳情彈窗並重設翻譯狀態。
     - `closeDetail()`: 關閉詳情彈窗。
     - `translateDetail()`: 呼叫 `ClaudeService.translate()` 將說明翻譯為繁體中文。
     - `clearDetailTranslation()`: 還原顯示原文。

2. **已修改的畫面結構 (`app.html`)**：
   - 移除了代理人卡片與技能卡片中的行內簡介與舊版 `translate-btn` 按鈕。
   - 分別為代理人卡片（[app.html:L263-267](src/app/app.html#L263-L267)）與技能卡片（[app.html:L282-285](src/app/app.html#L282-L285)）新增了「查看詳情」按鈕：
     ```html
     <!-- 代理人卡片 -->
     <button class="detail-btn"
       (click)="$event.stopPropagation();
                openDetail({id:a.id, label:'代理人', name:'@'+a.name, description:a.description, type:'agent'})">
       查看詳情
     </button>

     <!-- 技能卡片 -->
     <button class="detail-btn"
       (click)="openDetail({id:s.id, label:'技能', name:'/'+s.name, description:s.description, type:'skill'})">
       查看詳情
     </button>
     ```

---

## 🛠 待完成的開發工作

### 1. 在 `app.html` 結尾加入 Detail Modal 的 HTML 標記
需要將詳情彈窗的結構放到 [app.html](src/app/app.html) 的最尾端（例如在第 373 行上方，即 `</div>` 結束前）。

建議使用的範本結構如下：

```html
  <!-- ── 詳情 Modal ──────────────────────────────────── -->
  @if (detailItem()) {
    <div class="modal-backdrop" (click)="closeDetail()">
      <div class="modal" (click)="$event.stopPropagation()">
        <div class="modal-header">
          <span>ℹ️ {{ detailItem()!.label }}詳情</span>
          <button class="icon-btn" (click)="closeDetail()">✕</button>
        </div>
        <div class="modal-body">
          <div class="detail-name" style="font-size: 18px; font-weight: 600; color: #d4a853; margin-bottom: 8px;">
            {{ detailItem()!.name }}
          </div>
          
          <div class="detail-desc-box" style="background: #1f1f1f; padding: 12px; border-radius: 6px; border: 1px solid #2a2a2a;">
            <div class="desc-content" style="white-space: pre-wrap; line-height: 1.6; font-size: 13px;">
              {{ detailTranslation() !== null && detailTranslation() !== ''
                  ? detailTranslation()
                  : (detailItem()!.description || '（無說明）') }}
              @if (detailTranslation() === '') {
                <span class="translating">翻譯中…</span>
              }
            </div>
          </div>
        </div>
        <div class="modal-footer">
          @if (detailItem()!.description) {
            <button class="btn-secondary" 
              [disabled]="detailTranslation() === ''"
              (click)="detailTranslation() !== null ? clearDetailTranslation() : translateDetail()">
              {{ detailTranslation() === '' ? '…' : detailTranslation() !== null ? '還原原文' : '翻譯成繁體中文' }}
            </button>
          }
          <button class="btn-primary" (click)="closeDetail()">關閉</button>
        </div>
      </div>
    </div>
  }
```

### 2. 在 `app.scss` 中加入相關樣式
在 [app.scss](src/app/app.scss) 中加入對應樣式。因為此彈窗與設定（Settings Modal）的結構高度一致，大部分 `.modal-backdrop` 與 `.modal` 樣式皆可直接複用，主要需處理以下部分：
- `.detail-btn` 的按鈕外觀（可使用細邊框與小字級，使其在側欄卡片中不會過於突兀）。
- Modal 內部的 `detail-name` 與 `detail-desc-box` 排版與顏色微調。

---

## 📂 相關檔案快速連結
- 📄 組件邏輯：[app.ts](src/app/app.ts)
- 📄 畫面結構：[app.html](src/app/app.html)
- 📄 樣式檔案：[app.scss](src/app/app.scss)
- 📄 後端服務：[claude.service.ts](src/app/claude.service.ts)
